# 文档索引

整理日期：2026-05-30

## 当前入口

- `../project_overview.md`：项目总览与当前研究定位。
- `../current_status.md`：当前状态和下一步优先级。
- `../todo.md`：只保留待执行任务和共同纪律。
- `../experiment_log.md`：精简实验日志索引。
- `../final_reproduction_report.md`：PANDA 复现实验阶段报告。
- `../diagnostic_paper_report_draft.md`：诊断型论文 / fallback 草稿。
- `PANDA_SOTA冲刺与论文实验总方案.md`：Round12-R15 总方案，区分 SOTA 冲榜线、ADWA-PANDA 单模型方法线、OOF utility calibration 门控线和最终 test 冻结协议；当前执行结论以 `../current_status.md` 和 `../experiment_log.md` 为准。
- `当前领域方法路线与PANDA突破口.md`：当前版领域方法路线、模块架构、优缺点与 PANDA 后续突破口。
- `跨领域可借鉴方法与PANDA迁移方案.md`：从医学影像、遥感、工业缺陷、自动驾驶、推荐/因果、RAG/事实核验等领域迁移到 PANDA 的候选机制。
- `PANDA模块第一性原理审计与架构重组建议.md`：结合现有实验规律，对 PANDA baseline 每个模块做第一性原理审计，并给出模块替换、架构重组和 Round9 候选赛马建议。
- `创新方案第一性原理复审与更优方法建议.md`：对 Evidence-Gated / Aux-to-Final 当前主线做反审，记录 CUE-PANDA / BUA-PANDA 的 Round9-Round10 方案推导；当前执行结论以 `../current_status.md` 和 `../experiment_log.md` 为准。
- `round11_uea_panda_ablation_plan.md`：记录 UEA-PANDA 融合消融计划；当前执行结论为 D4 diagnostic-only，不打开 D5，详见 `../experiment_log.md`。

## 归档

- `archive/full_snapshots_20260528/root/`：2026-05-28 整理前根目录文档完整快照。
- `archive/method_rounds/`：R2-R7 方法方案、源码审计、验证深度复审和赛马协议。
- `archive/planning_and_submission/`：投稿规划、早期路线、阅读笔记和 CS-PANDA gate。
- `archive/registries/`：Round 6 / Round 7 候选登记表。
- `archive/word_docs/`：DOCX 与备份。

## 日志证据

主要证据仍在 `../remote_panda_work/repro_logs/` 和 `../remote_panda_work/logs/`。最新已完成闭环是 Round12-R15 当前作用域：Round12 证据在 `../remote_panda_work/repro_logs/round12_ensemble_val_audit/`，Round13 证据在 `../remote_panda_work/repro_logs/round13_adwa_d35_gradient_sanity/seed42/` 与 `../remote_panda_work/repro_logs/round13_adwa_d4/seed42/summary/`，Round14 证据在 `../remote_panda_work/repro_logs/round14_oof_launch_gate/`。上传 GitHub 时只同步摘要、manifest、metrics、notes 和必要 stdout；不上传 checkpoint、权重、原始数据、大 `.npz`、压缩包或含样本正文的预测长表。
