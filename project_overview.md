# PANDA 复现项目总览

最后整理：2026-05-28  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/project_overview.md`

## 项目定位

本项目复现 PANDA：Prototype-driven Asymmetric Neighbor-Domain Adaptation for Fake News Detection，并在复现基础上探索中文多模态、多领域假新闻检测中的可靠性、领域迁移和 final-boundary 改造方法。

当前结论很明确：复现与诊断证据已经完整；方法创新阶段尚无 `Primary-Candidate`。后续只推进已经出现正向线索、且能按 train/val-only 协议进一步验证的候选。

## 当前入口

- 当前状态：`current_status.md`
- 待办清单：`todo.md`
- 精简实验日志：`experiment_log.md`
- 复现实验报告：`final_reproduction_report.md`
- 诊断型论文草稿：`diagnostic_paper_report_draft.md`
- 文档索引：`docs/README.md`
- 历史长文归档：`docs/archive/README.md`

## 复现结论

PANDA 已在 Weibo-21 与 Weibo 上完成 paper-aligned 三 seed 复现，显式使用 `--model_name FTmodel`，参数为 batch size 32、learning rate `1e-4`、epoch 50、early stop 6，seeds 为 42、2024、2026。

| Dataset | Method | Macro-F1 | Accuracy | AUC |
| --- | --- | ---: | ---: | ---: |
| Weibo-21 | PANDA reproduced | 0.9474 +/- 0.0073 | 0.9474 +/- 0.0073 | 0.9879 +/- 0.0014 |
| Weibo | PANDA reproduced | 0.9415 +/- 0.0034 | 0.9415 +/- 0.0034 | 0.9866 +/- 0.0011 |

相对 PANDA paper reported，AUC 基本对齐，Macro-F1 / Accuracy 低约 0.95 到 1.16 个百分点。单 seed 尤其 seed42 会高估稳定性，正式表述必须使用三 seed mean +/- sample std。

## Reproduced Baselines

MMDFND、DAMMFND 也已完成两数据集三 seed reproduced baseline。方法论文或诊断论文的主表只使用 reproduced baseline，不混入 paper reported baseline。

| Dataset | Method | Macro-F1 | Accuracy | AUC |
| --- | --- | ---: | ---: | ---: |
| Weibo-21 | MMDFND | 0.9262 +/- 0.0147 | 0.9263 +/- 0.0147 | 0.9676 +/- 0.0114 |
| Weibo-21 | DAMMFND | 0.9436 +/- 0.0075 | 0.9436 +/- 0.0075 | 0.9839 +/- 0.0049 |
| Weibo-21 | PANDA | 0.9474 +/- 0.0073 | 0.9474 +/- 0.0073 | 0.9879 +/- 0.0014 |
| Weibo | MMDFND | 0.9094 +/- 0.0243 | 0.9094 +/- 0.0243 | 0.9719 +/- 0.0089 |
| Weibo | DAMMFND | 0.9374 +/- 0.0028 | 0.9374 +/- 0.0028 | 0.9856 +/- 0.0012 |
| Weibo | PANDA | 0.9415 +/- 0.0034 | 0.9415 +/- 0.0034 | 0.9866 +/- 0.0011 |

写作边界：PANDA 是当前 setting 下 strongest reproduced baseline；相比 DAMMFND 的优势较小，paired bootstrap CI 跨 0 时不要写显著优于。

## 方法创新状态

已验证过的旧路线包括 CS-PANDA / CLIP 图文冲突、Reliability-aware selector、uncertainty stable-source、R3 regret router、R4 non-self source intervention、Round 2 final-boundary/offline adapters、Round 3 branch-boundary residual、Round 4 first-principle boundary rebuild、Round 5 training dynamics、Round 6 auxiliary / branch / prompt / prototype / source-mixture 系列，以及 Round 7 的 D2/D3、D3.5 和 D4-lite。

共同规律：

- 可靠性、uncertainty、branch conflict、low-margin 等信号确实能解释错误或定位 hard region。
- 很多信号一旦变成 offline proxy、selector、adapter 或 inference-time reweighting，就被 original final、confidence-only、ordinary combiner、random/shuffled control 或 static aux control 打穿。
- 旧 PAD/source/prompt/prototype/selector 路线不能直接续参；如果重开，必须换本质机制并新建 manifest。
- D2/D3 只能否定当前 probe/offline/frozen 变体；D3.5/D4-lite 只能说明梯度可达和短训趋势；训练期方法至少需要 D4 seed42 smoke，稳定性至少需要 D5 三 seed val。

## 下一轮候选

下一轮只登记“有提升线索、值得更深验证”的 R8 队列，不代表已经有主方法。

1. R8-A / R7-A formal D4：Boundary-Risk Aware Training。现有 R7-A composite risk 在 D4-lite 中优于 deterministic-lite、confidence-only、random/shuffled risk controls，但正式 D4 尚未解锁。
2. R8-B：Static/Adaptive Auxiliary-Supervision Strength。`aux_weight_2p0` 在 R5-A smoke 与 R7-D lite 中反复显示为强 control / candidate signal，但不能包装成 R5-A 或 R6-A 成功。
3. R8-C：Training-time low-margin margin/risk regularizer。R6-C seed42 有弱正，但 seed2024 负、seed2026 被 calibration control 打穿，必须先补梯度 sanity。
4. R8-D：Branch aux-logit endogenous boundary signal。P2-B 曾有离线弱正，但 Round 3 被 ordinary combiner 打穿；若重开必须证明训练期内生版本打过 stacking / weighted-average controls。
5. R8-E：Confidence-uncertainty stable-source calibration add-on。只能在已有 D4 primary 后作为 second-stage add-on，不能独立做 primary。

## 实验纪律

- 三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。
- 所有 PANDA 命令必须显式 `--model_name FTmodel`。
- 新候选必须记录 `claim_scope / level_reached / required_level_for_exclusion / status_scope`。
- 日志仓库同步前必须排除 checkpoint、权重、原始数据集、服务器凭据、token、私钥、大 `.npz` 和含样本正文的预测长表。

## 远端与日志

远端活代码路径：

```bash
ssh panda-autodl
cd /root/autodl-tmp/panda_repro/panda
```

公开日志仓库：

```text
https://github.com/CmmmMMM407/PANDA-FUXIAN
```

本地 `remote_panda_work/` 是远端日志、代码片段和结果文件的证据副本，不视为最新活代码仓库。
