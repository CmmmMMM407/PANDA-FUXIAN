# TODO

最后整理：2026-05-30  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/todo.md`

## P0：R8 有希望方法验证队列

这些候选只表示“已有提升线索，值得更深验证”，不表示已有 `Primary-Candidate`。所有任务默认 train/val-only；三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。

- [x] **R8-A / R7-A formal D4：Boundary-Risk Aware Training**
  已完成 Weibo-21 seed42 train/val-only 5-epoch formal D4。结论 `No-Go`：best primary `r8a_composite_risk_primary` F1/Acc/AUC `0.926767/0.926829/0.978847`，没有打过 best strong control `shuffled_risk_control` 的 `0.938207/0.938211/0.980836`。

- [x] **R8-A 强对照**
  deterministic_train、same-budget CE、static aux 2.0、focal loss、class-balanced CE、confidence-only risk、random risk、shuffled risk、risk-margin only、risk-consistency only、risk-margin + consistency 已跑完，并输出 summary/manifest/decision。

- [x] **R8-A Go/No-Go**
  `No-Go`，原因 `best_primary_not_above_best_strong_control`。不进入 D5。

- [x] **R8-B：Static/Adaptive Auxiliary-Supervision Strength**
  已将 `aux_weight_2p0 / static-aux-strength` 从 R6-A control 独立登记为 R8-B。Seed42 D4 formal moat 结论 `Feasible-A`：static aux 2.0 F1/Acc/AUC `0.939837/0.939837/0.981407`，打过 deterministic、random/shuffled label、same-budget、PCGrad/CAGrad/GradNorm/DWA controls。

- [x] **R8-B formal D4 / D5**
  D4 已补齐 GradNorm/DWA moat；D5 三 seed val 复核完成，结论 `D5-Feasible-B-not-stable-enough`。三 seed static aux 2.0 均高于 deterministic，平均 Macro-F1 delta `+0.004856`，但 seed2026 被 `generic_dwa` 打穿：static aux `0.911679/0.912195`，generic DWA `0.926826/0.926829`。不能升 `Primary-Candidate`。

- [x] **R8-C：Training-time low-margin margin/risk regularizer**
  D3.5 gradient sanity 已完成，结论 `D3.5-No-Go-for-current-regularizer`。Primary 只在 `1/5` batch 产生非零 final-boundary 梯度，且低 margin 梯度富集不高于 controls；不打开 D4。

- [x] **R8-D：Branch Aux-Logit Endogenous Boundary Signal**
  D3.5 train-only sanity 已完成，结论 `D3.5-No-Go-for-current-aux-logit-signal`。Primary 可触达 final boundary，但 high-mismatch 梯度富集没有打过 controls；不打开 D4。

- [x] **R8-E：Confidence-uncertainty stable-source calibration add-on**
  本轮不启动。R8-A/C/D 未过线；R8-B 虽 seed42 D4 `Feasible-A`，但 D5 未能升 `Primary-Candidate`，因此没有可挂载的 primary。

## P0：Round9 / CUE-PANDA 候选验证队列

当前推荐主线来自 `docs/创新方案第一性原理复审与更优方法建议.md`：把 `Evidence-Gated Final Boundary + Aux-to-Final Meta Weighting` 升级为 `CUE-PANDA / Counterfactual Utility-aligned Evidence PANDA`。核心不是继续用 uncertainty/confidence heuristic 做 gate，而是先用 train-only counterfactual branch utility 监督 evidence gate，再用同一 utility 信号组织 aux-to-final training。

所有任务继续默认 train/val-only；D5 三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。

- [x] **Round9-A / CUE D2 Counterfactual Utility Probe**
  已完成 Weibo-21 seed42 train/val-only frozen/offline D2。结论 `No-Go-for-current-CUE-D2`：`cue_gate` F1/Acc/AUC `0.921800/0.921951/0.980069`，低于 `confidence_only_gate` `0.930045/0.930081/0.983659` 和 `same_param_mlp_classifier` `0.936542/0.936585/0.949355`；flip audit 为 W2C `8`、C2W `29`。

- [x] **Round9-A D2 strong controls**
  已比较 original equal-sum、global branch weights、confidence-only gate、uncertainty/disagreement gate、CUE gate、random/shuffled utility、same-param MLP、final+aux stacking、Platt/temperature。`final_aux_stacking` 与 `platt_temperature` 均为 `0.954451/0.954472`，接近原始 equal-sum `0.956086/0.956098`，强于 CUE。Oracle val utility diagnostic 达到 `0.973959/0.973984/0.998773`，说明 utility 本身有上界信号，但当前 train-only CUE gate 泛化失败；不进入 CUE D3.5/D4/D5。

- [x] **Round9-B / CUE D3.5 Gradient Sanity**
  已按门控关闭。Round9-A D2 已 `No-Go-for-current-CUE-D2`，因此当前 CUE 变体不启动 D3.5。

- [x] **Round9-B / CUE D4 seed42 training smoke**
  已按门控关闭。D3.5 未打开，因此当前 CUE D4 不启动。

- [x] **Round9-B / CUE D5 three-seed val**
  已按门控关闭。当前 CUE D4 未打开，继续禁止 test 参与任何选择。

- [x] **Round9-C / DGL-Aux PANDA 降级候选**
  已完成 Weibo-21 seed42 train/val-only D4 smoke。结论 `No-Go-for-current-DGL-Aux`：best DGL `round9c_dgl_branch_conflict_drop_aux1p0` F1/Acc/AUC `0.933299/0.933333/0.981650`，低于 `static_aux_weight_2p0_anchor_control` `0.939837/0.939837/0.981407`、`generic_dwa` `0.938210/0.938211/0.980962`、deterministic/same-budget/detached `0.936585/0.936585/0.983765`；flip audit W2C `15`、C2W `17`，不打开 D5。

## P0：Round10 / BUA-PANDA 融合候选验证队列

Round10 新主线来自 `docs/创新方案第一性原理复审与更优方法建议.md` 的 BUA-PANDA 方案：融合 R8-B static aux 2.0、Round9-A oracle counterfactual utility 和 R7/R8 boundary-risk。核心不是继续让 utility 做 inference gate，而是把 utility 降级为 training-time branch auxiliary supervision allocator；boundary-risk 只作为 trust gate；static aux 2.0 作为 anchor。

所有任务继续默认 train/val-only；D5 三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。

- [x] **Round10-A / BUA D2.5 offline allocator simulation**
  已完成 Weibo-21 seed42 train/val-only offline allocator 诊断。结论 `D2.5-No-Go-for-current-BUA-boundary-gate`：primary `bua_boundary_gated_utility_aux` expected utility `0.773082`，高于 static anchor `0.503536`、shuffled utility `0.539701`、random utility `0.508881`、reverse utility `0.468324`、confidence-only allocation `0.505511`，但低于 utility-only `0.911898` 和 entropy-only `0.816022`。原因 `boundary_gate_not_proven_vs:bua_utility_only_aux_alloc,bua_entropy_gated_utility_aux`。证据：`remote_panda_work/repro_logs/round10_bua_d25/seed42/`。

- [x] **Round10-A D2.5 strong controls**
  已比较 uniform static aux allocation、utility-only allocation、boundary-only allocation、entropy-only gate、random utility、shuffled utility、reverse/negative utility、shuffled boundary-risk、confidence-only branch allocation。真实 utility 信号与 shuffled/random/reverse/confidence controls 分离，但当前 boundary gate 没有证明增量贡献，因此当前 BUA 不进入 D3.5。

- [x] **Round10-B / BUA D3.5 gradient sanity**
  已按门控关闭。Round10-A D2.5 未证明 boundary-gated allocation 优于 utility-only / entropy-only ablations，因此当前 BUA 不启动训练图梯度 sanity。

- [x] **Round10-C / BUA D4 seed42 training smoke**
  已按门控关闭。D3.5 未打开，当前 BUA D4 不启动；继续禁止 test 参与任何选择。

- [x] **Round10-C D4 strong controls / moat**
  已按门控关闭。当前 D4 不启动，因此 D4 moat 不执行；若未来重开，需要保留 deterministic、same-budget、static aux 2.0、DWA/GradNorm/PCGrad/CAGrad、detached aux、utility-only、boundary-only、shuffled/random/reverse utility 与 shuffled boundary-risk controls。

- [x] **Round10-D / BUA D5 three-seed val**
  已按门控关闭。当前 BUA D4 未打开，不启动 D5；继续禁止 test 参与任何选择。

- [x] **Round10-E / Source-CUE reserve**
  继续关闭。BUA 当前未进入 D4，未来只有 CUE-family 至少 D4 有正向趋势，或 forced source utility D2 直接证明 source marginal utility 优于 PAD/random/shuffled/reverse/bottom controls，才重开 source utility 线。

## P0：Round11 / UEA-PANDA 消融验证队列

Round11 新主线是 `UEA-PANDA / Utility-Entropy Anchored Auxiliary PANDA`。它不再把 Round10 失败的 low-margin/high-risk boundary hard gate 作为 trust gate，而是把 R8-B 的 static aux 2.0 作为同预算 anchor，把 Round9/Round10 的 counterfactual branch utility 作为训练期 per-sample branch auxiliary allocation 方向，并用 utility entropy 做 soft reliability/calibration。

所有任务继续默认 train/val-only；D5 三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。

- [x] **Round11-A / UEA D4 seed42 消融 smoke**
  已完成 Weibo-21 seed42 5 epoch train/val-only。结论 `Utility-Entropy-Aux-Diagnostic-only`：primary `uea_entropy_alpha0p5` F1/Acc/AUC `0.921905/0.921951/0.981142`，低于 static aux 2.0 `0.939837/0.939837/0.981407`、generic DWA `0.938210/0.938211/0.980962`，flip net `-9`。Best real UEA ablation `uea_entropy_alpha0p25` 为 `0.938207/0.938211/0.983977`，接近 DWA 但仍低于 static aux 2.0。

- [x] **Round11-A controls / moat**
  已在同一 summary 比较 R6/R8 strong controls 与 UEA utility controls。关键负证据：`uea_reverse_utility_entropy_alpha0p5` 达到 `0.939837/0.939837/0.982084`，与 static aux 2.0 并列最高，说明当前 per-sample utility 方向性没有被证明；`uea_boundary_entropy_alpha0p5` 仅 `0.923574/0.923577/0.979397`，继续证明 Round10 boundary gate 不是可复用抓手。

- [x] **Round11-A Go/No-Go**
  `No-Go-to-D5`。Decision reasons：`best_uea_not_above_required_controls:static_aux_weight_2p0_anchor_control`、`primary_not_best:best=uea_reverse_utility_entropy_alpha0p5`、`best_uea_macro_f1_moat_lt_delta`。当前 UEA 只能写成 `utility/entropy auxiliary allocation diagnostic`，不能升 `Primary-Candidate`。

- [x] **Round11-B / D5 三 seed val 复核（门控）**
  已按门控关闭。Round11-A 未打过 static aux 2.0 与 reverse-utility control，不启动三 seed D5；继续禁止 test 参与选择。

## P0：Round12-R15 / SOTA 冲刺与论文实验总方案

总方案见 `docs/PANDA_SOTA冲刺与论文实验总方案.md`。本轮已把 **SOTA 冲榜线** 和 **论文方法线** 分开闭环：Round12 完成 train/val-only ensemble 上界诊断，Round13 完成 `ADWA-PANDA / Anchored Dynamic Auxiliary-supervision PANDA` D3.5/D4，Round14 完成 OOF utility calibration 启动门控，Round15 按门控关闭。

所有任务继续默认 train/val-only；最终配置冻结前不导出、不打开、不分析 test。

- [x] **Round12-A / 模型资产与 logits 盘点**
  已完成 train/val-only 资产盘点。安全可用资产包括 PANDA reproduced、static aux 2.0、generic DWA 的 seeds `42/2024/2026` train/val artifacts；DAMMFND/MMDFND 仅发现不完整/非当前安全池 artifacts，未纳入主 ensemble。证据：`remote_panda_work/repro_logs/round12_ensemble_val_audit/round12_asset_manifest.csv`。

- [x] **Round12-B / 缺失 train/val logits 安全导出**
  已补齐 PANDA reproduced、static aux 2.0、generic DWA 三 seed train/val logits/probability exports；未导出 test。证据：`remote_panda_work/repro_logs/round12_trainval_exports/` 与 `remote_panda_work/repro_logs/round12_ensemble_val_audit/round12_decision_summary.json`。

- [x] **Round12-C / Ensemble 上界与 diversity audit**
  已完成 equal-logit、nested convex、nested calibration、oracle any-correct 与 pairwise diversity audit。Strongest single 为 `panda_reproduced_seed42` F1/Acc/AUC `0.954457/0.954472/0.987573`；best non-oracle ensemble 为 `panda_dwa_equal_logit` `0.956090/0.956098/0.988197`；oracle PANDA+DWA any-correct 达 `0.983736/0.983740`。

- [x] **Round12-D / SOTA 冲榜线 Go/No-Go**
  `Diagnostic-only-No-Go-to-Round15`。Best non-oracle ensemble 相对 strongest single Macro-F1 delta `+0.001633`，低于 `+0.002`；paired bootstrap CI 跨 0，`p_delta_le_0=0.417`。可写作 ensemble/selection-space diagnostic，不能冻结进 Round15。

- [x] **Round13-A / ADWA-PANDA 设计与 manifest**
  已实现 ADWA-PANDA 并写入 manifest。实现约束：static aux 2.0 作为总预算 anchor，DWA 只调 text/image/fusion auxiliary branches 相对权重，加入 clip、mean normalize、final-loss guard；final CE 不纳入 DWA；不使用 boundary hard gate。

- [x] **Round13-B / ADWA D3.5 gradient sanity**
  已完成 train-only D3.5，结论 `D3.5-Feasible-A`。ADWA 梯度触达 `h_final`、`final_classifier`、branch features 和 aux heads；无 optimizer step、无 checkpoint、无 val/test。证据：`remote_panda_work/repro_logs/round13_adwa_d35_gradient_sanity/seed42/`。

- [x] **Round13-C / ADWA D4 seed42 smoke**
  已完成 Weibo-21 seed42 5 epoch train/val-only D4，结论 `D4-No-Go-to-D5`。Best ADWA `adwa_clip_1p0_2p5` F1/Acc/AUC `0.933331/0.933333/0.980645`，低于 static aux 2.0 `0.939837/0.939837/0.981407` 和 generic DWA `0.938210/0.938211/0.980962`。

- [x] **Round13-D / ADWA D5 三 seed val 复核（门控）**
  已按门控关闭。Round13-C 未同时打过 static aux 2.0 与 generic DWA，且 best ADWA 低于 deterministic `0.936585`，不启动 D5。

- [x] **Round14-A / OOF Utility Calibration 启动判定**
  已完成 launch gate，结论 `Round14-A-No-Go-to-B-C-current-assets`。Round12 存在 oracle selection space（oracle gap `+0.029279`），但 learned ensemble 不够稳；Round13 ADWA D4 no-go；当前未发现 split-safe OOF utility target。

- [x] **Round14-B / OOF utility target 与 split-safe meta learner**
  已按 Round14-A 门控关闭，未启动。旧 Round9 `branch_utility_train.csv` 被明确标记为 train-only not-out-of-fold，`branch_utility_val_diagnostic.csv` 不能用于 target；禁止把旧 CUE/UEA utility CSV 伪装成 OOF target。

- [x] **Round14-C / OOF utility controls / moat**
  已按 Round14-A 门控关闭，未启动。Platt/temperature、final+aux stacking、confidence-only gate、shuffled/reverse/random utility、static aux 2.0、generic DWA 均可作为历史 diagnostic controls，但缺 split-safe OOF target，因此不进入 moat。

- [x] **Round15 / 冻结配置与最终 test 协议（门控）**
  已按门控关闭，未启动 final freeze/test。Round12 no-go to Round15，Round13 no-go to D5，Round14 no-go to B/C；当前仍无可冻结三 seed val 配置，test 继续未打开。

## P0：共同执行纪律

- [x] 所有 PANDA 训练命令显式 `--model_name FTmodel`。
- [x] 所有正式候选先写 manifest，记录 `allowed_splits=["train","val"]`、`test_split_exported=false`、`test_used_for_decision=false`。
- [x] 每个结论写清 `claim_scope / level_reached / required_level_for_exclusion / status_scope`。
- [x] D2/D3 只否定当前 probe/offline/frozen 变体；D3.5/D4-lite 只作为梯度可达和短训趋势；D4 才能判当前训练实现；D5 才能判稳定性。
- [x] No-Go checkpoint 默认可回收；长期保留 manifest、stdout、metrics、summary、notes、flip audit、telemetry，不同步 checkpoint、权重、原始数据、大 `.npz` 或含样本正文的预测长表。

## P1：文档与日志同步

- [x] 保全 2026-05-28 整理前完整文档快照：`docs/archive/full_snapshots_20260528/root/`。
- [x] 将历史方案、投稿规划、阅读笔记、Word 文档、候选登记表移动到 `docs/archive/`。
- [x] 将根目录入口文档压缩为当前状态 / TODO / 精简日志 / 报告。
- [x] 将整理后的文档和筛选后的实验日志同步到 GitHub 仓库 `CmmmMMM407/PANDA-FUXIAN`，提交 `d94253b`。
- [x] 同步前扫描敏感信息，确认不包含服务器密码、token、私钥、完整 SSH 连接串、checkpoint、权重或原始数据集。

## 已完成主线索引

详细完成记录已归档到完整旧版 TODO；这里只保留索引。

- [x] PANDA Weibo-21 / Weibo 三 seed 复现。
- [x] MMDFND / DAMMFND 两数据集三 seed reproduced baseline。
- [x] Reliability / uncertainty / selector stability / statistical diagnostics。
- [x] CS-PANDA、Reliability-aware selector、uncertainty stable-source、R3、历史 R4、P0/P1、Round 2、Round 3、Round 4、Round 5、Round 6 当前作用域验证。
- [x] Round 7 D2/D3、D3.5 和 R7-A/R7-D D4-lite。
- [x] Round 8 A/B/C/D formal/D3.5/D5 当前作用域验证。
- [x] Round 9 CUE D2 与 DGL-Aux D4 当前作用域验证。
- [x] Round 10 BUA D2.5 当前作用域验证；后续 D3.5/D4/D5 按门控关闭。
- [x] Round 11 UEA D4 消融当前作用域验证；后续 D5 按门控关闭。
