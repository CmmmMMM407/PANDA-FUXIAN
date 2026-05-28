# PANDA 复现与可靠性诊断报告草稿

日期：2026-05-25

状态说明（2026-05-28 更新）：Round 6/7 当前作用域验证已闭环；新的待执行规划入口见 `current_status.md` 和 `todo.md`。Round 7 历史规划已归档到 `docs/archive/method_rounds/新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 与 `docs/archive/registries/round7_candidate_registry.md`。本文仍只作为 reproduced baseline、失败边界和 reliability/uncertainty 诊断证据池，不是当前主方法草稿。

状态说明（2026-05-26 更新）：本文件只作为方法论文的证据池、失败边界分析和 fallback 草稿，不是当前主线。Round 4 first-principle boundary rebuild、Round 5 Gate-0 与 R5-A 单项 seed42 smoke 均已完成；R5-A 结论为 `No-Go`，当前没有 `Primary-Candidate`，不复核 seeds、不扩 Weibo、不看 test。最新执行口径见 `current_status.md`、`todo.md` 与归档方法文档。

## 一句话结论

本项目已经完成 PANDA、MMDFND、DAMMFND 在 Weibo-21 与 Weibo 上的 reproduced 三 seed 对比。PANDA 仍是 reproduced baseline 中整体最强模型，尤其在 AUC、ECE、Brier 和高置信错误率上优于 MMDFND / DAMMFND；但后续 selector 创新实验没有形成稳定性能闭环。因此本文件只作为 empirical diagnostic / reproducibility / reliability analysis 的备份写法和证据整理：

```text
Reproduced Baselines + Reliability and Uncertainty Diagnostics + Selector Stability Analysis + Boundary Conditions of Reliability-aware Neighbor Selection
```

## 推荐题目

英文：

```text
Reliability and Uncertainty Diagnostics for Neighbor-domain Adaptation in Multimodal Fake News Detection
```

中文：

```text
面向多模态假新闻检测的邻域迁移可靠性与不确定性诊断
```

## Research Questions

RQ1: How reproducible and reliable are PANDA, MMDFND, and DAMMFND under a two-dataset, three-seed setting?

RQ2: Which uncertainty signals predict errors and high-confidence errors?

RQ3: Does stochastic neighbor selection affect prediction stability?

RQ4: Why do reliability-aware selector variants fail to close the performance loop?

## 贡献表述

1. A reproduced two-dataset, three-seed benchmark for multimodal fake news detection, covering PANDA, MMDFND, and DAMMFND.
2. A reliability/uncertainty diagnostic showing that confidence and fusion uncertainty explain errors better than CLIP image-text conflict.
3. A selector stability and boundary-condition analysis showing that signal validity does not imply selector-level performance gain.

注意：这里不写 method contribution。

## 论文结构

1. Reproduced Baselines
2. Reliability and Uncertainty Diagnostics
3. Selector Stability Analysis
4. Boundary Conditions of Reliability-aware Neighbor Selection
5. Discussion

## Reproduced Baselines

主表只使用 reproduced 三 seed test mean +/- sample std，不混入 paper reported baseline。

| Dataset | Method | Macro-F1 | Accuracy | AUC |
| --- | --- | ---: | ---: | ---: |
| Weibo-21 | MMDFND | 0.9262 +/- 0.0147 | 0.9263 +/- 0.0147 | 0.9676 +/- 0.0114 |
| Weibo-21 | DAMMFND | 0.9436 +/- 0.0075 | 0.9436 +/- 0.0075 | 0.9839 +/- 0.0049 |
| Weibo-21 | PANDA | 0.9474 +/- 0.0073 | 0.9474 +/- 0.0073 | 0.9879 +/- 0.0014 |
| Weibo | MMDFND | 0.9094 +/- 0.0243 | 0.9094 +/- 0.0243 | 0.9719 +/- 0.0089 |
| Weibo | DAMMFND | 0.9374 +/- 0.0028 | 0.9374 +/- 0.0028 | 0.9856 +/- 0.0012 |
| Weibo | PANDA | 0.9415 +/- 0.0034 | 0.9415 +/- 0.0034 | 0.9866 +/- 0.0011 |

写作口径：PANDA is the strongest reproduced baseline in our setting。不要写 PANDA significantly outperforms DAMMFND，除非正文同时报告 paired bootstrap 不显著这一事实。

证据文件：

- `remote_panda_work/repro_logs/reproduced_baseline_main_table/reproduced_baseline_main_table.md`
- `remote_panda_work/repro_logs/reproduced_baseline_main_table/reproduced_baseline_main_table_full.csv`
- `remote_panda_work/repro_logs/reproduced_baseline_main_table/reproduced_baseline_by_seed.csv`

## Reliability Diagnostics

PANDA 在两个数据集上均有最低的 ECE、Brier 和 high-confidence error rate。这是当前最稳的可靠性发现。

| Dataset | Method | ECE | Brier | HCE Rate |
| --- | --- | ---: | ---: | ---: |
| Weibo-21 | MMDFND | 0.0546 +/- 0.0030 | 0.0656 +/- 0.0106 | 0.0488 +/- 0.0016 |
| Weibo-21 | DAMMFND | 0.0340 +/- 0.0077 | 0.0476 +/- 0.0090 | 0.0293 +/- 0.0114 |
| Weibo-21 | PANDA | 0.0255 +/- 0.0066 | 0.0418 +/- 0.0054 | 0.0233 +/- 0.0009 |
| Weibo | MMDFND | 0.0476 +/- 0.0041 | 0.0722 +/- 0.0130 | 0.0430 +/- 0.0090 |
| Weibo | DAMMFND | 0.0307 +/- 0.0122 | 0.0490 +/- 0.0050 | 0.0271 +/- 0.0095 |
| Weibo | PANDA | 0.0211 +/- 0.0085 | 0.0440 +/- 0.0034 | 0.0196 +/- 0.0048 |

正式 weak-domain 分析使用 val-defined weak domains，来自 `conflict_gate_by_domain.csv` 和 `conflict_gate_summary.json`：

- Weibo：国际、经济、教育。
- Weibo-21：灾难事故、科技、医药健康。

Test-derived 弱域只能作为探索性说明或附录，不用于正文方法选择：

- Weibo：政治 Macro-F1 0.8328，科学 0.8506，军事 0.8542。
- Weibo-21：科技 Macro-F1 0.9123，医药健康 0.9151，社会生活 0.9211。

证据文件：

- `remote_panda_work/repro_logs/panda_diagnostics/reliability_summary.csv`
- `remote_panda_work/repro_logs/panda_diagnostics/per_domain_metrics_summary.csv`
- `remote_panda_work/repro_logs/mmdfnd_diagnostics/reliability_summary.csv`
- `remote_panda_work/repro_logs/dammfnd_diagnostics/reliability_summary.csv`

## Statistical Diagnostics

已补纯 pandas/numpy 统计模块，输出 paired hierarchical bootstrap、McNemar exact sign-test 近似和 uncertainty gate 显著性摘录。配对覆盖率为 100%，配对键包含 dataset、seed、content、title、image、category、label 和 duplicate index。

PANDA vs DAMMFND：

| Dataset | Metric | Delta PANDA-DAMMFND | 95% CI | p |
| --- | --- | ---: | ---: | ---: |
| Weibo-21 | Macro-F1 | 0.0038 | [-0.0114, 0.0201] | 0.660 |
| Weibo-21 | Accuracy | 0.0038 | [-0.0114, 0.0201] | 0.699 |
| Weibo-21 | AUC | 0.0037 | [-0.0028, 0.0113] | 0.349 |
| Weibo | Macro-F1 | 0.0041 | [-0.0039, 0.0121] | 0.296 |
| Weibo | Accuracy | 0.0041 | [-0.0039, 0.0121] | 0.313 |
| Weibo | AUC | 0.0023 | [-0.0022, 0.0055] | 0.396 |

PANDA vs MMDFND：

- Weibo-21 Macro-F1 delta 0.0212, 95% CI [0.0085, 0.0342], paired bootstrap p=0.000.
- Weibo Macro-F1 delta 0.0321, 95% CI [0.0086, 0.0530], paired bootstrap p=0.000.
- Reliability metrics ECE/Brier/HCE also favor PANDA over MMDFND on both datasets with CIs below 0.

统计结论：

- PANDA 相比 MMDFND 的优势稳健。
- PANDA 相比 DAMMFND 是 strongest reproduced baseline，但优势幅度小且 paired bootstrap CI 跨 0；正文不要写显著优于 DAMMFND。

证据文件：

- `tools/generate_statistical_diagnostics.py`
- `remote_panda_work/repro_logs/statistical_diagnostics/statistical_diagnostics_summary.md`
- `remote_panda_work/repro_logs/statistical_diagnostics/paired_bootstrap_model_comparisons.csv`
- `remote_panda_work/repro_logs/statistical_diagnostics/paired_match_coverage.csv`
- `remote_panda_work/repro_logs/statistical_diagnostics/uncertainty_gate_significance_extract.csv`

## Uncertainty Signal Gate

CLIP-only 图文冲突信号不强，因此不能强写“图文语义冲突导致 PANDA 错误”。

| Dataset | Split | CLIP-only error AUC | Full conflict error AUC | Confidence-uncertainty error AUC |
| --- | --- | ---: | ---: | ---: |
| Weibo | val | 0.5087 | 0.7463 | 0.8589 |
| Weibo-21 | val | 0.5314 | 0.8515 | 0.8768 |
| Weibo | test | 0.4748 | 0.8007 | 0.8933 |
| Weibo-21 | test | 0.5572 | 0.8200 | 0.9013 |

解释：

- Full conflict 比 CLIP-only 强，但主要来自 branch disagreement、fusion uncertainty、confidence-uncertainty。
- Confidence-uncertainty 往往比 full conflict 更强，说明当前证据更像 reliability / uncertainty diagnostic，而不是独立图文冲突因果。
- Random control 接近随机，说明诊断信号不是纯噪声；但它仍不足以证明 selector 方法有效。

证据文件：

- `remote_panda_work/repro_logs/panda_diagnostics/gate_signal_significance.csv`
- `remote_panda_work/repro_logs/panda_diagnostics/reliability_disagreement_conclusion.md`

## Selector Stability Analysis

Prediction-level repeated-forward 诊断显示，PANDA 的 Gumbel selector 随机性会传导到最终 `y_score`，并造成少量预测翻转；deterministic selector 可把推理期方差压到浮点噪声级。

| Variant | Split | mean y_score std | p95 y_score std | Flip rate | Neighbor change |
| --- | --- | ---: | ---: | ---: | ---: |
| PANDA Gumbel reproduced | val | 0.001278 | 0.008946 | 0.005962 | 1.0 |
| PANDA Gumbel reproduced | test | 0.001272 | 0.008865 | 0.002168 | 1.0 |
| Deterministic reproduced | val | 4.90e-08 | 1.79e-07 | 0 | 0 |
| Deterministic reproduced | test | 4.82e-08 | 1.79e-07 | 0 | 0 |
| Winning control short5 | val | 4.97e-08 | 1.79e-07 | 0 | 0 |
| Winning control short5 | test | 4.99e-08 | 1.79e-07 | 0 | 0 |

写作边界：

- 可以说 Gumbel neighbor selector 是 eval-time prediction variance 的来源之一。
- 可以说 deterministic selector 是必要强对照。
- 不能说 winning control 因为方差近零而方法成功；近零方差只是关闭随机 selector 的预期结果。

证据文件：

- `remote_panda_work/repro_logs/prediction_repeated_forward_variance/repeated_forward_aggregate_summary.csv`
- `remote_panda_work/repro_logs/prediction_repeated_forward_variance/notes.md`

## Boundary Conditions of Reliability-aware Neighbor Selection

Selector v2 Go/No-Go 和 seed-recheck 都不支持把 clean branch/fusion reliability selector 写成正式方法。

Seed42 Go/No-Go 中，唯一 val 过线的是：

```text
confidence_uncertainty + stable_source_reward + pre_epoch + lambda=0.2
```

但它是 uncertainty control，不是 clean branch/fusion disagreement。且 seed-recheck 后不稳定：

| Split | Variant | Macro-F1 mean/std | Acc mean/std | AUC mean | ECE mean | pass_count |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| val | deterministic_eval_l0 | 0.9371 / 0.0034 | 0.9371 / 0.0034 | 0.9828 | 0.0242 | 0 |
| val | winning control | 0.9360 / 0.0049 | 0.9360 / 0.0050 | 0.9842 | 0.0235 | 2 |
| test | deterministic_eval_l0 | 0.9414 / 0.0072 | 0.9415 / 0.0071 | 0.9865 | 0.0141 | 0 |
| test | winning control | 0.9420 / 0.0095 | 0.9420 / 0.0095 | 0.9856 | 0.0212 | 0 |

关键反例：

- seed2024 上 winning control val/test F1、Acc、AUC、ECE、Brier、HCE、弱域 F1 均未优于 deterministic。
- seed-recheck test `pass_count=0/3`，不能作为主方法胜出证据。
- Clean branch/fusion variants 在 val/test 多数低于 deterministic reference。

证据文件：

- `remote_panda_work/repro_logs/innovation_training_v2_go_nogo_eval/go_nogo_decision_summary.csv`
- `remote_panda_work/repro_logs/innovation_training_v2_seed_recheck_eval/seed_recheck_aggregate_summary.csv`
- `remote_panda_work/repro_logs/innovation_training_v2_seed_recheck_eval/seed_recheck_run_level_summary.csv`

## Method-Candidate Race Summary

2026-05-26 已完成 R3、历史 R4、P0-B、P1-A、P1-B、P1-C、Round 2 P2-A/P2-B/P2-C/P2-D、Round 3 branch-boundary residual、Round 4 first-principle boundary rebuild、Round 5 Gate-0 以及 R5-A 单项 seed42 smoke。当前没有 `Primary-Candidate`；P2-B `final+aux logits` residual adapter 已被 Round 3 强对照复核降级为 ordinary-combiner risk evidence，R5-A image projection 也因低于 deterministic 且被 `aux_weight_2p0` control 打穿而 `No-Go for current r5a_image_project_l1p0 training implementation`。后续若继续方法线，必须提出本质不同的新候选并重新 Gate-0；D0/D1/D2/D3 的历史负证据不能永久排除方法族。

| Candidate | Gate conclusion | Paper use |
| --- | --- | --- |
| R3 regret/reliable routing | self-domain route collapse; non-self utility cannot enter boundary | failed current R3 v0 routing implementation / self-domain-collapse evidence |
| R4 non-self source-view intervention | source views weakly perturb logits, but shuffled/random/bottom controls explain effects | source-view boundary condition |
| P0-B DCA/source-view risk | DCA/source prompts weakly affect logits, but PAD-ranked sources do not beat controls | DCA sensitivity caveat |
| P1-A feature-aware PAD | source set changes, but feature ranking is beaten by shuffled/random/bottom controls | source-ranking boundary condition |
| P1-B domain-conditioned expert gate | checkpoint has 2 task gates, not 9 domain gates | implementation/code-path caveat |
| P1-C reliability extension | seed42 val passes, but three-seed val mean F1/Acc is below deterministic; seed2024 fails | calibration/diagnostic evidence |

P1-C 的关键数字：seed42 val 的 confidence-uncertainty stable-source variant F1/Acc/AUC 为 `0.941395/0.941463/0.984960`，但三 seed val mean F1/Acc 为 `0.936018/0.936043`，低于 deterministic `0.937093/0.937127`。这说明 uncertainty/reliability 可以作为诊断信号，但目前不能作为稳定主方法。

证据文件：

- `remote_panda_work/repro_logs/p1c_reliability_extension_gate/p1c_reliability_extension_decision_summary.md`
- `remote_panda_work/repro_logs/p1c_reliability_extension_gate/p1c_seed_recheck_val_run_summary.csv`
- `docs/archive/method_rounds/创新方案赛马总控与实施协议.md`

## 推荐图表

正文优先：

- `remote_panda_work/repro_logs/panda_diagnostics/per_domain_macro_f1.svg`
- `remote_panda_work/repro_logs/panda_diagnostics/reliability_brier.svg`
- `remote_panda_work/repro_logs/panda_diagnostics/selector_jaccard_change.svg`

附录优先：

- `remote_panda_work/repro_logs/panda_diagnostics/domain_neighbor_heatmap_weibo21_test_deterministic_topk.svg`
- `remote_panda_work/repro_logs/panda_diagnostics/domain_neighbor_heatmap_weibo21_test_selected_gumbel.svg`
- `remote_panda_work/repro_logs/panda_diagnostics/domain_neighbor_heatmap_weibo_test_deterministic_topk.svg`
- `remote_panda_work/repro_logs/panda_diagnostics/domain_neighbor_heatmap_weibo_test_selected_gumbel.svg`
- `remote_panda_work/repro_logs/panda_diagnostics/high_confidence_errors_extended.csv`

## 对实验思路的启发

1. PANDA 复现结果说明 neighbor-domain adaptation 的排序能力仍强，但离散 F1/Acc 对 seed 和 selector 随机性敏感。
2. 可靠性信号确实存在：confidence-uncertainty、fusion uncertainty、branch disagreement 与错误、高置信错误、弱域表现有关。
3. 信号有效不等于 selector 方法有效。当前大量 reranking 能改变 neighbor set，却未稳定改变最终标签或改善三 seed 主指标。
4. 后续若重新做方法，应该把“可靠性改善”和“分类性能提升”分开建模：先证明 ECE/Brier/HCE/弱域改善，再设计能稳定传导到 F1/Acc 的训练目标。
5. Selection margin 的真实边界应是 topS-top(S+1)，不是 top1-top2；这是本轮实现里最有保留价值的机制洞察。
6. Weibo offline lambda=0.0 是重要边界条件：不能把方法外推成所有数据集都有 re-ranking 收益。

## 当前不建议写的表述

- 不写 “image-text conflict causes PANDA errors”。
- 不写 “Reliability-aware Disagreement PANDA achieves stable improvements”。
- 不写 “uncertainty-aware stable-source selection is the proposed final method”。
- 不用 seed42 单点提升替代三 seed seed-recheck。
- 不把 repeated-forward 近零方差包装成 winning control 成功。
