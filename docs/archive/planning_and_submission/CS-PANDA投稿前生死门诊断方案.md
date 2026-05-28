# CS-PANDA 投稿前生死门诊断方案

日期：2026-05-23

## 目的

状态更新（2026-05-28）：本文档是 CS-PANDA / CLIP 图文冲突因果线的历史 gate 记录，不代表当前待执行主线。Round 6/7 当前作用域验证已闭环且没有 `Primary-Candidate`；新的待执行规划入口已切到 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md`、`round7_candidate_registry.md`、`round7_gate0_manifest_TEMPLATE.json` 和 `todo.md`。未达到足够验证深度的本质不同训练期机制仍不得永久排除。

状态更新：本 gate 已在 2026-05-23 完成。实际结果不支持强 CLIP 图文冲突因果线。历史上项目主线曾降级为 **Reliability-aware Multimodal Disagreement Selection**，但该线、后续 uncertainty-aware stable-source、R3/历史 R4、Round 1、Round 2、Round 3、Round 4、Round 5 Gate-0、R5-A 单项 smoke 与 Round 6/7 当前作用域验证均未产生 `Primary-Candidate`。本文档保留为预注册诊断流程和证据链记录，不代表当前主线；截至 2026-05-28，新的规划入口是 Round 7 `Risk-Aware Final-Boundary Learning`。

原 CS-PANDA 核心假设是：

> 多模态假新闻检测中，领域迁移是否可靠不仅取决于 domain similarity，也取决于目标样本与候选邻域之间的图文冲突模式是否匹配。

这个假设经 gate 后没有获得足够支持。现有结果显示 CLIP-only 接近随机，而 branch disagreement、fusion uncertainty、confidence-uncertainty 更能解释错误。因此，后续不按强 CS-PANDA 故事投稿。

历史执行结论：当时曾转向 reliability-aware multimodal disagreement selection，并用 deterministic selector、confidence-uncertainty-only、fusion-only、branch-only、overconfidence-only 和 random control 做强对照。该线后续已 No-Go，只保留为证据池。

## 本轮审稿意见评估

本轮意见整体合理，应全部采纳。它指出的核心风险不是方法不可做，而是当前证据链仍可能被审稿人质疑为“看了 test 错误后设计方法”或“用模型置信度包装成图文冲突”。因此，本诊断方案的定位从普通误差分析升级为投稿前预注册 gate：先固定 split 使用规则、conflict score 定义、统计检验和通过阈值，再运行 val-based gate；test 只做最终确认性分析。

不需要反驳的部分：

- 避免 test-set overfitting：合理，且是正式论文可信度的底线。
- Full conflict 不能用 `is_error` 监督：合理，否则会退化成错误检测器。
- AUC 通过线需带 bootstrap CI 和 permutation test：合理，防止 AUC 0.58-0.60 的偶然波动被过度解释。
- High-confidence error enrichment 需报告 count、平滑 odds ratio、Fisher exact test 或 bootstrap CI：合理，因为高置信错误样本比例只有约 1.5%-2.5%。
- Per-domain 相关性只能作为辅助：合理，Weibo/Weibo-21 的 domain 数较少，相关系数不稳。
- Neighbor selection 字段应尽早导出：合理，CS-PANDA 的贡献必须落在邻域迁移行为改变上，而不是只证明 conflict 与错误相关。
- Fusion uncertainty 定义必须统一：使用 entropy 或 `1 - abs(2 * p_fusion - 1)`，确保数值越大表示越不确定；不得使用方向相反的 `abs(p_fusion - 0.5)`。
- Full conflict 第一版应优先采用 z-score 后等权无监督组合，val 调权只作为附录或消融，避免被认为在 val 上学习错误检测分数。
- 统计检验优先使用 domain-stratified bootstrap 或 seed-aware bootstrap；单纯 sample bootstrap 可能低估同一批样本三 seed 预测相关性带来的不确定性。
- 两层 gate 的执行顺序必须拆清楚：第一层是投稿前 pre-method signal gate；第二层可以是基于已导出 PAD/neighbor logits 的 minimal/offline selector behavior gate，或在实现最小 selector 后作为 mechanism gate。后续新方法训练只能在第一层通过或明确降级叙事后进行。
- 正式弱域不能由 test predictions 选择。正式 gate 中的弱域必须由 train/val baseline 的 bottom-k domain F1 或 top-k domain error rate 预先确定，test 只验证这些域是否仍然偏弱。
- Confidence 负对照需要拆为 confidence-uncertainty 与 overconfidence-only：前者是 `1 - max(y_score, 1-y_score)`，后者是 `max(y_score, 1-y_score)`，尤其 high-confidence error 富集必须和 overconfidence-only 区分开。

## 数据缺口状态

历史缺口：早期本地 `remote_panda_work/repro_logs/*_test_predictions.csv` 只有最终预测与样本元信息，已确认包含：

- `y_true`
- `y_score`
- `y_pred`
- `category_id`
- `category_name_from_loader`
- `content` / `post_text`
- `image` / `image_id`

现有文件不包含：

- `p_text`
- `p_image`
- `p_fusion`
- `clip_text_image_cos`
- `clip_dissimilarity`
- `fusion_uncertainty`
- `selected_neighbor_domains`
- `neighbor_logits`

当前状态：该缺口已补齐。远端已重新导出 train / val / test 三个 split 的扩展 prediction 文件，并完成 val-based gate 与 test confirmatory analysis。后续不需要重复导出同一批字段，除非要补 prediction-level repeated-forward `y_score` variance。

```bash
ssh panda-autodl
cd /root/autodl-tmp/panda_repro/panda
```

## 必须导出的字段

每个 split、每个样本至少导出：

| 字段 | 说明 |
| --- | --- |
| `sample_id` | 样本索引或原始 id |
| `dataset` | Weibo / Weibo-21 |
| `seed` | 42 / 2024 / 2026 |
| `split` | train / val / test |
| `category_id` | 领域 id |
| `category_name` | 领域名 |
| `y_true` | 标签 |
| `y_score` | PANDA 主输出概率 |
| `y_pred` | PANDA 主预测 |
| `p_text` | 文本分支输出概率 |
| `p_image` | 图像分支输出概率 |
| `p_fusion` | 融合分支输出概率 |
| `clip_text_image_cos` | CN-CLIP text/image cosine similarity |
| `clip_dissimilarity` | `1 - clip_text_image_cos` |
| `branch_disagreement` | `abs(p_text - p_image)` |
| `fusion_uncertainty` | `1 - abs(2 * p_fusion - 1)` 或 entropy；数值越大表示越不确定 |
| `is_error` | `y_pred != y_true` |
| `is_high_conf_error` | `is_error and max(y_score, 1-y_score) >= 0.9` |

可选导出：

- 原始 PANDA selected neighbors。
- PAD similarity matrix 中当前样本 target domain 对各 source domain 的 logits。
- deterministic top-k neighbors。
- repeated eval 下的 neighbor selection frequency。

这些 neighbor 字段应尽早导出。仅证明 conflict 与错误相关，还不足以证明它应该调制邻域迁移；必须观察弱域/高冲突样本是否存在邻域选择不稳定、邻域 logits 接近、或反复选择疑似不合适邻域的问题。

## 数据使用红线

- Gate 阶段的规则、阈值、full-conflict 权重、prototype 构建和任何超参选择只能使用 train/val。
- Test split 只能用于最终确认性分析和最终主表，不能参与 conflict 权重调节、prototype 构建或方法选择。
- 不得用 test error 反推方法设计。
- Conflict prototype 只能由 train 或 train+val 构建，不能使用 test label。
- 若 full conflict 使用可学习 MLP，不得用 `is_error` 或 `is_high_conf_error` 作为监督训练目标；否则它会变成错误检测器，而不是图文冲突信号。
- Gate 阶段优先使用无监督组合，例如 z-score 后等权的 `clip_dissimilarity + branch_disagreement + fusion_uncertainty`。Val 调权只能作为附录或消融，不作为第一版主结果。
- 在打开 test 确认结果前，应先保存 `conflict_gate_config.yaml` 或同等配置文件，记录特征定义、标准化方式、组合权重、阈值、bootstrap 次数、permutation 次数和通过规则。
- 若 full conflict 权重需要搜索，只能在 train/val 上搜索；最终用于 test 的权重必须由 val gate 锁定并写入 `val_selected_conflict_weights.json`。

## Conflict Score 候选

必须区分独立信号与模型自反馈信号：

| 名称 | 公式 | 风险 | 用途 |
| --- | --- | --- | --- |
| CLIP-only | `clip_dissimilarity` | 相对独立，但 CLIP 可能不敏感 | 最重要的外部图文冲突证据 |
| Branch-only | `abs(p_text - p_image)` | 模型自反馈 | 只能作为辅助 |
| Uncertainty-only | `fusion_uncertainty` | 置信度再包装 | 只能作为辅助 |
| Full conflict | z-score 后等权无监督组合；正式方法可用不以 `is_error` 监督的 MLP/embedding | 需要消融证明，严禁错误标签泄漏 | 方法主信号 |
| Confidence-uncertainty | `1 - max(y_score, 1-y_score)` 或主分支 entropy | 容易变成校准/不确定性方法 | 必须作为反证 baseline |
| Overconfidence-only | `max(y_score, 1-y_score)` | 只衡量主分类器过度自信 | high-confidence error 分析的必要反证 |
| Random conflict | 打乱 conflict score | 负对照 | 验证不是随机噪声 |

实现时，`p_text`、`p_image`、`p_fusion` 用于 conflict feature 时必须优先使用 detach 版本，避免模型通过自反馈捷径优化 selector。

## 生死门指标

### 1. Error-vs-Correct 区分能力

计算每种 conflict score 对 `is_error` 的 AUC：

```text
AUC_conflict_error = AUC(is_error, conflict_score)
```

最低通过线：

- CLIP-only 或 Full conflict 的 AUC >= 0.58，且 bootstrap 95% CI 下界不能明显跨过 0.5。
- Full conflict 必须高于 confidence-uncertainty、overconfidence-only 和 random conflict。
- 必须提供 permutation test，验证 AUC 高于随机打乱标签/分数不是偶然。

较强通过线：

- Full conflict AUC >= 0.62。
- high-confidence error 上 AUC 更高或 top-quantile enrichment 明显。
- Full conflict 的 95% CI 不跨 0.5，且 permutation p-value < 0.05。

### 2. High-confidence Error 富集

按 conflict score 分位数分组，比较 top 25% 与 bottom 25% 的高置信错误率：

```text
enrichment = high_conf_error_rate(top25) / high_conf_error_rate(bottom25)
```

最低通过线：

- enrichment >= 1.5。
- 或 top25 高置信错误率显著高于整体均值。
- 必须同时报告 top/bottom quartile 的样本数和高置信错误数。
- 必须报告带平滑的 odds ratio、Fisher exact test 或 bootstrap CI，避免高置信错误样本稀疏导致倍率虚高。

### 3. Sample-level 控制领域后的区分能力

Per-domain 数量较少，相关系数容易不稳。因此更强的 gate 是 sample-level 分析：

- 在控制 domain 后，conflict score 是否仍能预测 `is_error`。
- 在控制 domain 后，conflict score 是否仍能预测 `is_high_conf_error`。

建议实现：

- 分 domain 计算 error-vs-correct AUC，再做宏平均。
- Logistic regression：`is_error ~ conflict_score + domain fixed effects`。
- 或在每个 domain 内做 conflict score 分位数分组，再合并检验。

最低通过线：

- 控制 domain 后，conflict score 仍有正向预测力。
- 至少在一个数据集上，domain-macro AUC 或 fixed-effect coefficient 趋势清楚。

### 4. 弱域 vs 强域差异

正式弱域定义：

- 在查看 test confirmatory 结果前，根据 train/val baseline 的 per-domain Macro-F1 或 error rate 选择弱域。
- 默认使用 val split、三 seed mean 的 bottom-3 domain F1；如 val 样本过少，可用 train+val 的 domain error rate 做稳定性核验。
- 现有 test predictions 得出的弱域只作为探索性提示，不参与正式弱域选择。

探索性弱域提示：

- Weibo-21：科技、医药健康、社会生活。
- Weibo：政治、科学、军事。

检查：

- 弱域错误样本 conflict score 是否高于强域正确样本。
- 弱域 conflict score 均值是否高于强域。
- per-domain conflict score 是否与 per-domain error rate 正相关。
- Test split 只验证 train/val 预先确定的弱域是否仍然偏弱，不重新挑选弱域。

最低通过线：

- 弱域错误样本 conflict score 均值高于强域正确样本。
- 至少一个数据集上 per-domain conflict/error 相关为正且趋势清楚。
- 该项只作为辅助证据，不能作为唯一 gate 通过依据。

### 5. 统计检验

建议同时报告：

- Mann-Whitney U test。
- Cohen's d。
- Bootstrap confidence interval。
- Domain-stratified bootstrap。
- Seed-aware bootstrap。
- Permutation test。
- Fisher exact test 或带平滑 odds ratio，用于 high-confidence error enrichment。

最低要求：

- 不只看均值差，必须报告效应量或置信区间。
- AUC=0.58-0.60 但 CI 跨 0.5 时，只能算边缘通过，不能进入强 CS-PANDA 叙事。
- 单纯 sample bootstrap 只能作为辅助。正式 gate 优先报告 domain-stratified 或 seed-aware bootstrap，避免低估三 seed 相关预测的不确定性。

## 两层 Gate 结构

### 第一层：Conflict Signal Gate

目的：证明 conflict score 和错误/高置信错误存在稳定关系。

最低通过线：

- CLIP-only 或 full conflict 对 `is_error` 的 AUC 达到最低线，且 CI 不明显跨 0.5。
- Full conflict 高于 confidence-uncertainty、overconfidence-only 和 random conflict。
- High-confidence error 在高 conflict 分位上有富集，并报告 count、平滑 odds ratio 和 Fisher exact test 或 bootstrap CI。
- 控制 domain 后，conflict score 仍有正向预测力。

解释规则：

- 若 CLIP-only 显著，且 full conflict 优于负对照，可以主张 cross-modal conflict-aware selection。
- 若 CLIP-only 不显著，但 branch disagreement / uncertainty 显著，只能降级为 multimodal disagreement / reliability-aware selection，不能强写“图文冲突导致错误”。

### 第二层：Selector Behavior Gate

目的：证明 reliability/disagreement-aware selector 不只是提高分数，而是实际改变了邻域迁移行为。

执行方式分两种：

- Minimal/offline selector behavior gate：在完整方法训练前，使用已导出的 PAD/neighbor logits、domain reliability prototypes 和 z-score 等权 reliability/disagreement score，离线模拟 reliability-aware re-ranking 或 deterministic top-k 变化。
- Post-implementation mechanism gate：在第一层通过并实现最小 reliability-aware selector 后，比较训练后的 selector 行为。

必须比较原始 PANDA selector、deterministic selector 和 offline/minimal reliability-aware selector：

- High-disagreement / high-uncertainty 样本的 selected-neighbor Jaccard change。
- Selection entropy 或 repeated eval selection frequency 变化。
- PAD/neighbor logits 的 topS-top(S+1) boundary margin 或候选邻域 margin；PANDA 当前选 top-2，因此重点看 top2-top3。
- 弱域样本的 neighbor selection frequency 是否从不稳定/疑似负迁移邻域转向更一致的邻域。
- Domain-to-neighbor heatmap 和 disagreement-conditioned heatmap。

最低通过线：

- High-disagreement 样本的 neighbor Jaccard change 明显高于 low-disagreement 样本，或 selector entropy / selection frequency 出现清晰变化。
- 弱域样本至少在一个数据集上出现可解释的 selection frequency 变化。
- PAD/neighbor margin 或 repeated eval variance 至少有一个稳定性指标改善。

如果第一层通过但第二层不通过，论文不能把贡献写成 neighbor-domain adaptation 机制创新，只能写成可靠性诊断或弱化为辅助 reweighting。历史上 Reliability-aware Disagreement PANDA 训练前至少应完成第一层 pre-method signal gate；第二层可先用 offline selector 作为投稿前机制可行性 gate，再用 post-implementation mechanism gate 作为论文证据。当前实际结果显示后续 selector v2 与 seed-recheck 未通过，因此本项目不再按该方法主线推进。

## 推荐执行顺序

1. 远端活代码仓库导出 train/val/test 扩展 predictions，字段至少覆盖分支概率、CLIP cosine、conflict features 和 neighbor selection 记录。
2. 在不查看 test label 诊断结论的前提下，固定 `conflict_gate_config.yaml`。
3. 只用 train/val 计算 conflict feature 标准化参数、full-conflict 权重、conflict prototype 和 gate 通过判断。
4. 由 train/val baseline bottom-k domain F1 或 top-k error rate 固定正式弱域。
5. 先运行第一层 pre-method conflict signal gate。
6. 若第一层通过或边缘通过，再用 PAD/neighbor logits 运行 minimal/offline selector behavior gate。
7. 再运行 test confirmatory analysis；test 结果只用于确认和最终报告，不再反向改定义。
8. 若第一层不通过，停止强 CS-PANDA 当前主线，转向 deterministic/stability、reliability-aware disagreement 或 leave-one-domain 泛化。该条为历史预注册分岔；当前这些方向已进一步验证并归档，Round 3 Branch-Boundary Residual、Round 4 First-Principle Boundary Rebuild、Round 5 Gate-0 与 R5-A 单项 smoke 均已完成且未产生 `Primary-Candidate`。
9. 若第一层和 offline 第二层均通过，再实现最小 reliability-aware selector，并用 post-implementation mechanism gate、neighbor heatmap、selection frequency 和弱域样本案例证明邻域迁移行为确实改变。

## 生死门结论规则

### 通过

满足以下条件：

- Full conflict 或 CLIP-only 能明显区分错误/高置信错误。
- Full conflict 优于 confidence-uncertainty、overconfidence-only 和 random conflict。
- 弱域错误样本有更高 conflict score 或更明显 top-quantile enrichment。
- Selector behavior gate 显示 high-conflict/弱域样本的邻域选择行为确实改变。
- 结果主要来自 val gate，test 只做确认，且没有用 test label 调权。

后续动作：

- 若 CLIP-only 同时显著，理论上可实现 CS-PANDA；本项目实际结果不满足该条件。
- 历史执行中曾转向 Reliability-aware Disagreement PANDA；但 selector v2 clean branch/fusion No-Go，winning-control seed-recheck 也未通过，当前结论应降级为 reliability/uncertainty diagnostic + failed selector analysis。

### 边缘通过

满足以下条件：

- Full conflict 有弱区分能力，但主要来自 branch disagreement / uncertainty。
- CLIP-only 不强。
- AUC 点估计达到门槛但 CI 跨 0.5，或 high-confidence enrichment 因样本稀疏不稳定。
- Selector behavior 有变化但不稳定，或只在一个数据集/部分 seed 上明显。

后续动作：

- 不保留强 CS-PANDA 因果表述。
- 强调 reliability-aware multimodal disagreement，而不是纯图文错配。
- 若 CLIP-only 不强，则将方法叙事降级为 reliability-aware multimodal disagreement selection。
- 必须加强消融和 heatmap 证明 selector 行为确实变化。

### 不通过

出现以下情况：

- Full conflict 不优于 random conflict。
- Full conflict 只等价于 confidence-uncertainty 或 overconfidence-only。
- 弱域错误与 conflict score 无明显关系。
- Selector behavior gate 不显示邻域选择变化。

后续动作：

- 不按 CS-PANDA 当前故事投稿。
- 转向 deterministic neighbor selection + reliability analysis。
- 或补 leave-one-domain 泛化，改写为稳定跨域泛化方法。

## 必须输出的文件

建议生成：

- `conflict_gate_config.yaml`
- `val_selected_conflict_weights.json`
- `conflict_gate_summary.json`
- `conflict_gate_val_summary.json`
- `conflict_gate_test_confirmatory.json`
- `conflict_gate_by_dataset.csv`
- `conflict_gate_by_domain.csv`
- `conflict_gate_domain_controlled.csv`
- `reliability_score_error_groups.csv`
- `high_conf_error_cases.csv`
- `neighbor_selection_diagnostics.csv`
- `reliability_score_distribution.png`
- `domain_reliability_error_correlation.png`

这些文件应同步到日志仓库，但不得包含原始图片、checkpoint、权重或敏感信息。

## 结论

新方法不是先实现再找解释。正确顺序是：

1. 导出 conflict diagnostics。
2. 用 train/val 固定正式弱域、conflict 定义、统计检验和通过线。
3. 在 train/val 上运行第一层 pre-method conflict signal gate。
4. 用导出的 PAD/neighbor logits 做第二层 minimal/offline selector behavior gate。
5. 用 test 只做最终确认。
6. 通过后再实现最小 reliability-aware selector，并用 post-implementation mechanism gate 和 neighbor heatmap 证明迁移行为改变。
7. 最后用主表和可靠性指标证明性能与稳定性收益。

## 2026-05-23 实际 Gate 结果

远端已完成扩展诊断导出和 gate 分析，产物位于：

```text
/root/autodl-tmp/panda_repro/panda/repro_logs/conflict_gate/
```

本地证据副本位于：

```text
remote_panda_work/repro_logs/conflict_gate/
```

已生成 18 个 `extended_predictions_{dataset}_seed{seed}_{split}.csv`，覆盖 Weibo-21 / Weibo、seeds 42 / 2024 / 2026、train / val / test。导出字段包含分支概率、CLIP cosine、conflict features、confidence controls、error flags、PAD/neighbor logits、selected neighbors、deterministic top-k 和 repeated eval frequency。

Val-based 弱域：

- Weibo：国际、经济、教育。
- Weibo-21：灾难事故、科技、医药健康。

Val-selected offline lambda：

- Weibo：0.0，`no_lambda_improved_val_selector_behavior`。
- Weibo-21：0.05，`smallest_lambda_with_val_high_conflict_jaccard_change_gap_improvement`。

Signal gate 关键结果：

| Split | Dataset | CLIP-only AUC | Full conflict AUC | Confidence-uncertainty AUC | Fusion uncertainty AUC |
| --- | --- | ---: | ---: | ---: | ---: |
| val | Weibo | 0.5087 | 0.7463 | 0.8589 | 0.8559 |
| val | Weibo-21 | 0.5314 | 0.8515 | 0.8768 | 0.8645 |
| test | Weibo | 0.4748 | 0.8007 | 0.8933 | 0.8769 |
| test | Weibo-21 | 0.5572 | 0.8200 | 0.9013 | 0.8752 |

结论：

- CLIP-only 未通过强图文冲突证据线，不能主张“CLIP 图文冲突导致 PANDA 错误”。
- Full conflict 对 `is_error` 有较强区分能力，但主要由 branch disagreement、fusion uncertainty 和 confidence-uncertainty 支撑。
- Confidence-uncertainty 强于 full conflict，说明该信号更像 reliability / uncertainty / disagreement 诊断，而不是独立图文冲突因果。
- Overconfidence-only 对 high-confidence error enrichment 呈反向或无效，说明高置信错误富集不是单纯“越自信越错”的现象。
- 按预注册规则，后续论文主线应降级为 **reliability-aware multimodal disagreement selection**。若要回到强 CS-PANDA，需要补出更强、独立于模型置信度的外部图文冲突证据。
