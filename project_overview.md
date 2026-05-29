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

已验证过的路线包括 CS-PANDA / CLIP 图文冲突、Reliability-aware selector、uncertainty stable-source、R3 regret router、R4 non-self source intervention、Round 2 final-boundary/offline adapters、Round 3 branch-boundary residual、Round 4 first-principle boundary rebuild、Round 5 training dynamics、Round 6 auxiliary / branch / prompt / prototype / source-mixture 系列、Round 7 的 D2/D3、D3.5 和 D4-lite、Round 8 formal/D3.5/D5、Round 9 CUE/DGL-Aux，以及 Round 10 BUA D2.5。

共同规律：

- 可靠性、uncertainty、branch conflict、low-margin 等信号确实能解释错误或定位 hard region。
- 很多信号一旦变成 offline proxy、selector、adapter 或 inference-time reweighting，就被 original final、confidence-only、ordinary combiner、random/shuffled control 或 static aux control 打穿。
- 旧 PAD/source/prompt/prototype/selector 路线不能直接续参；如果重开，必须换本质机制并新建 manifest。
- D2/D3 只能否定当前 probe/offline/frozen 变体；D2.5 只能决定是否打开训练图验证；D3.5/D4-lite 只能说明梯度可达和短训趋势；训练期方法至少需要 D4 seed42 smoke，稳定性至少需要 D5 三 seed val。

## 当前创新结论

当前 R8-R10 的最新结论如下，仍不代表已有主方法：

1. R8-A Boundary-Risk Aware Training formal D4 为 `No-Go`，被 shuffled risk control 打穿。
2. R8-B static aux 2.0 有跨 seed 正向趋势，但 D5 被 seed2026 DWA 打穿，只能作为训练动力学观察。
3. R8-C/R8-D D3.5 均未证明当前信号能形成干净训练收益，不打开 D4。
4. Round9 CUE D2 显示 oracle utility 有强上界，但 train-only CUE gate 泛化失败；Round9 DGL-Aux D4 被 static aux 2.0 / DWA 等强 controls 打穿。
5. Round10 BUA D2.5 显示 counterfactual utility 作为 aux allocation 信号干净，但当前 boundary trust gate 被 utility-only / entropy-only ablations 反超，不打开 D3.5/D4/D5。

若继续方法创新，下一步必须提出本质不同机制：解释 static aux 2.0、utility-only / entropy-only allocation 的训练动力学，并避免把 low-margin / risk 直接当 hard trust gate。

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
