# 实验日志

最后整理：2026-05-28  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/experiment_log.md`

本文件现在只保留高密度索引和最新关键实验摘要。逐条长日志、命令细节和历史流水账见完整快照与 `remote_panda_work/repro_logs/`。

## 2026-05-28：文档整理与日志同步准备

目标：

- 精简本地项目文档，合并重复入口，归档历史长文。
- 保留信息保真：先完整快照，再压缩根目录文档。
- 准备把整理后的实验日志同步到 GitHub 仓库 `CmmmMMM407/PANDA-FUXIAN`。

操作：

- 将整理前根目录 Markdown/JSON/DOCX 原样备份到 `docs/archive/full_snapshots_20260528/root/`。
- 将历史方案文档移动到 `docs/archive/method_rounds/`。
- 将投稿规划、路线和阅读笔记移动到 `docs/archive/planning_and_submission/`。
- 将候选登记表移动到 `docs/archive/registries/`。
- 将 Word 文档移动到 `docs/archive/word_docs/`。
- 将 `project_overview.md`、`current_status.md`、`todo.md`、`experiment_log.md` 重写为入口型短文档。

结果：

- 根目录保留当前入口、报告、manifest 和工具目录。
- 完整旧文档未删除，已进入快照和归档区。
- 敏感信息初筛未发现真实 SSH 连接串或密码落盘；同步时仍需排除 checkpoint、权重、原始数据、大 `.npz`、压缩包和含样本正文的预测长表。

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
