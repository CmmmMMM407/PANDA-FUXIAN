# TODO

最后整理：2026-05-28  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/todo.md`

## P0：R8 有希望方法验证队列

这些候选只表示“已有提升线索，值得更深验证”，不表示已有 `Primary-Candidate`。所有任务默认 train/val-only；三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。

- [ ] **R8-A / R7-A formal D4：Boundary-Risk Aware Training**
  冻结 Weibo-21 seed42 5-epoch manifest。现有线索：R7-A composite risk val error AUC `0.828231`，D3.5 risk-margin 可触达 final classifier / `h_final`，D4-lite `r7a_composite_risk_lite` F1/Acc/AUC `0.732329/0.739837/0.866367`，优于 deterministic-lite、confidence-only、random risk、shuffled risk controls。

- [ ] **R8-A 强对照**
  必须包括 deterministic_train、same-budget CE / no-new-signal、static aux 2.0、focal loss、class-balanced CE、confidence-only risk、random risk、shuffled risk、risk-margin only、risk-consistency only、risk-margin + consistency。输出 val metrics、flip audit、hard-bin / weak-domain summary、risk-bin summary 和 manifest。

- [ ] **R8-A Go/No-Go**
  Seed42 D4 primary 的 Macro-F1/Acc 不低于 deterministic，理想提升 `>= +0.3pp`；wrong->correct 大于 correct->wrong；low-margin、high-disagreement、weak-domain 至少不净负；AUC/ECE/Brier/HCE 至少两个不劣化；best strong control 不能追平或打穿。过线后才进入 D5 seeds 2024/2026 val 复核。

- [ ] **R8-B：Static/Adaptive Auxiliary-Supervision Strength**
  将 `aux_weight_2p0 / static-aux-strength` 独立登记为候选。现有线索：R5-A smoke 中 `aux_weight_2p0` F1/Acc `0.939837/0.939837` 高于 deterministic `0.938175/0.938211`；R7-D D4-lite 中 static aux 2.0 F1/Acc/AUC `0.736521/0.739837/0.837197` 明显高于 sample aux curriculum。

- [ ] **R8-B formal D4**
  预注册 static aux `0.5/1.0/1.5/2.0/3.0`、warmup/ramp schedule、branch-specific aux weights、detached/no-feature-update aux、same-budget controls、random aux labels、shuffled aux labels、generic PCGrad/CAGrad/GradNorm/DWA controls。通过线是打过 deterministic、random/shuffled label、same-budget 和 generic gradient controls，并解释 branch-to-final alignment 是否改善。

- [ ] **R8-C：Training-time low-margin margin/risk regularizer**
  只把 R6-C low-margin 线索改写为训练期 regularizer，不再做 offline adapter。先补 D3.5 gradient sanity，再决定是否开 D4 seed42。强对照包括 confidence-only low-margin、global calibration / Platt / temperature、focal loss、class-balanced CE、random low-margin mask、shuffled low-margin mask、all-sample margin regularizer。

- [ ] **R8-D：Branch Aux-Logit Endogenous Boundary Signal**
  重新登记 P2-B `final+aux logits` 弱信号为训练期内生机制。先补 D3.5 检查 detached branch logits/features、小 residual head、branch-logit distillation loss 是否触达 final boundary；强对照必须包括 weighted average final+aux、logistic stacking、final-only MLP、parameter-matched final-only head、random/shuffled aux logits、branch identity permutation、branch-drop ablation 和 same-budget controls。

- [ ] **R8-E：Confidence-uncertainty stable-source calibration add-on**
  只在 R8-A/R8-B/R8-C/R8-D 产生 D4 过线 primary 后作为 second-stage add-on。必须打过 overconfidence-only、random、deterministic、signed/asymmetric uncertainty controls。通过线为三 seed val F1/Acc 不下降且 ECE/Brier/HCE/weak-domain 至少两个稳定改善。

## P0：共同执行纪律

- [ ] 所有 PANDA 训练命令显式 `--model_name FTmodel`。
- [ ] 所有正式候选先写 manifest，记录 `allowed_splits=["train","val"]`、`test_split_exported=false`、`test_used_for_decision=false`。
- [ ] 每个结论写清 `claim_scope / level_reached / required_level_for_exclusion / status_scope`。
- [ ] D2/D3 只否定当前 probe/offline/frozen 变体；D3.5/D4-lite 只作为梯度可达和短训趋势；D4 才能判当前训练实现；D5 才能判稳定性。
- [ ] No-Go checkpoint 默认可回收；长期保留 manifest、stdout、metrics、summary、notes、flip audit、telemetry，不同步 checkpoint、权重、原始数据、大 `.npz` 或含样本正文的预测长表。

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
