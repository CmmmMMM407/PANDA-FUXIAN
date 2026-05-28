# PANDA 复现后创新规划

日期：2026-05-23

状态更新（2026-05-28）：本文档保留为早期创新规划历史记录，不代表当前待执行主线。Round 6/7 当前作用域验证已闭环且没有 `Primary-Candidate`；新的待执行规划入口已切到 Round 7 `Risk-Aware Final-Boundary Learning`，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md`、`round7_candidate_registry.md`、`round7_gate0_manifest_TEMPLATE.json` 和 `todo.md`。当前仍不训练、不复核 seeds、不扩 Weibo；Round 7 必须先做 artifact audit 与 D2/D3 核心机制实验。

## 文档用途

本文档用于规划 PANDA 复现完成后的创新修改方案。根据 2026-05-23 至 2026-05-24 的 gate 和 reproduced baseline 结果，创新方向曾收口为：

**Reliability-aware Multimodal Disagreement Selection for Multimodal Fake News Detection**

也可表述为：

- Reliability-aware Disagreement PANDA
- Reliability-aware PANDA
- Multimodal Disagreement-aware Stable PANDA
- Reliability-aware Stable Neighbor Selection

但 2026-05-24 selector v2 5-epoch Go/No-Go 后，clean branch/fusion disagreement 主线没有通过。seed42 一度出现的新候选方向是：

**Uncertainty-aware Stable Source Selection for Multimodal Fake News Detection**

该候选曾用简称：

- Uncertainty-aware Stable-source PANDA
- Uncertainty-aware Stable Neighbor Selection
- Reliable Stable-source PANDA

随后 Weibo-21 seeds 2024/2026 复核显示该候选也不稳定：seed2024 明确失败，三 seed val F1/Acc mean 低于 deterministic。当前不能把它写成正式方法；它只作为 reliability/uncertainty 证据和强对照，不能替代下一轮方法候选赛马。

2026-05-25 进一步尝试的 `R3-PANDA: Regret-Regularized Reliable Routing` 已完成 Weibo-21 seed42 gate，结论为 `No-Go for current D4 R3 v0`。R3 的正向 variants 未超过 deterministic，且 route 完全 self-domain collapse，说明当前不应继续在 R3 v0 上堆 `lambda`、group loss 或 reliability vector；全新 self-suppressed source mixture 需新 D2/D3 -> D4。

2026-05-25 曾切换的新候选方法路线为：

**R4-PANDA: Non-self Source-domain Intervention Consistency for Reliable Neighbor-domain Adaptation**

R4 的核心是显式构造 PAD top-k non-self source-domain intervention views，并用 view CE 与 anchor-view consistency 直接训练 final classifier boundary。四个子代理审查后已收紧：先做 frozen-view validity gate；通过后冻结 `r4_gate_config.yaml` 和 no-weight primary config；`L_worst`、CVaR、reliability weighting 只作二阶段消融。后续 frozen-view validity 已完成并判定 `No-Go for current D2 PAD-top2 forced-view validity / immediate-training permission`，因此 R4 只保留为历史候选与当前变体失败边界记录。

2026-05-25 已新增 `创新方案赛马总控与实施协议.md`。后续创新不再把单个候选预设为最终主线，而是以候选池赛马执行：R4、DCA/source-view risk、feature-aware PAD、domain gate 修正/消融、evidential/reliability extension 都必须先做最小可行性 gate。若某个方案先通过，只标记为可行，待全部候选赛完后再确定最终主线。

2026-05-26 最新口径经 2026-05-27 复审后改为：历史 R4、P0-B、P1-A 是当前 D2 probe No-Go，P1-B 是 `Blocked/current checkpoint unsupported`，P1-C 是当前 D4+D5 method No-Go；Round 2 P2-A/P2-B/P2-C/P2-D、Round 3 Branch-Boundary Residual 和 Round 4 First-Principle Boundary Rebuild 也已完成，但 D3 结论只覆盖当前 offline/frozen 变体。当前没有 `Primary-Candidate`，但这不是把论文主线改成诊断型报告。当前方法论文路线转向 Round 5 `Branch-Evidential Boundary Rebuilding` 候选池，详细方案以 `PANDA源码第一性原理审计与Round5方案升级.md` 和 Gate-0 manifest 为准。第一轮只做 Gate-0：

1. G0-A branch-final gradient conflict diagnostic。
2. G0-D low-margin boundary sensitivity diagnostic。
3. G0-E branch-to-final arbitration frozen probe。
4. G0-S sample-conditioned prompt/source interaction feasibility。

2026-05-26 Gate-0 已完成：G0-A `Feasible-A`，G0-D `Feasible-B`，G0-E `No-Go for current frozen arbitration probe`，G0-S `No-Go for current prompt/source probe`。深度复盘后已降调：G0-A 只能写成 image-branch/final gradient conflict candidate signal，不能声称 low-margin/weak-domain 机制已成立；G0-D 是 destructive boundary fragility，不是可直接训练的 boundary-stress 收益。随后 R5-A 单项 seed42 smoke 已完成并判定 `No-Go for current image projection training implementation`：primary 低于 deterministic，且被 `aux_weight_2p0` control 打穿。当前不解锁 `Boundary-Stressed Branch-Consistent PANDA`、R5-Prime 或 source/prompt 路线，不复核 seeds、不扩 Weibo、不看 test；R5-Prime/R5-A+D/R5-S 仍是 `Not-Unlocked`，不是组合机制永久失败。

2026-05-26 远端源码第一性原理审计后，Round 5 曾在 Gate-0 前进一步升级：新增 `PANDA源码第一性原理审计与Round5方案升级.md`，将候选池收紧为 `Branch-Evidential Boundary Rebuilding`。源码级断点包括 PAD/GNS 不可导与 self dominated、DCA 样本无关且进入太晚、prototype reconstruction 断梯度、aux branch 未内生进入 final arbitration。当时第一阶段新增：

5. G0-E branch-to-final arbitration frozen probe。
6. G0-S sample-conditioned prompt/source interaction feasibility。

Gate-0 后该条件已经被判定未满足：G0-E No-Go，G0-D destructive，G0-S No-Go。因此这条升级路线现在只作为历史预注册条件保留；当前不得进入 R5-Prime / R5-A+D seed42 smoke，也不得重开 source/domain prompt 路线。

未来新候选的执行顺序仍固定为 protocol freeze -> Gate-0 diagnostic -> seed42 smoke -> seeds 2024/2026 val recheck -> Weibo 扩展 -> final test confirmatory；但本轮 R5-A 已在 seed42 smoke 阶段 `No-Go`，因此不进入 seeds 2024/2026 val recheck、不扩 Weibo、不触碰 test。每个方案先做 train/val-only 最小 gate，失败立即切换，先可行也只标记为 `Feasible-A/B`，全部候选验证后再定主线。

原候选方向为：

**Conflict-aware Stable Neighbor-Domain Adaptation for Multimodal Fake News Detection**

原简称：

- CS-PANDA
- Conflict-aware Stable PANDA
- Conflict-aware Stable Neighbor-Domain Adaptation

核心判断：

- 单独做 deterministic selector 和 threshold calibration，容易被审稿人认为是后处理或工程修补。
- 强 CLIP 图文冲突因果线未通过 gate，不能作为主贡献。
- Reliability / uncertainty 与错误和高置信错误有更强相关性；selector v2 结果显示 branch/fusion disagreement 暂不适合作为主方法机制。
- 稳定邻域选择仍然重要，但应作为“可靠邻域迁移”的组成部分，而不是唯一主贡献。
- Domain-aware calibration 降级为可靠性分析模块，用 ECE、Brier score、repeated eval variance 支撑，而不作为核心创新点。
- 2026-05-23 二次审稿人视角评估后，CS-PANDA 被重新定位为“有潜力但未证实”的方案；2026-05-24 先从强 CS-PANDA 降级到 Reliability-aware Disagreement PANDA，随后 selector v2 Go/No-Go 又把 clean branch/fusion 主线降级为 uncertainty-aware stable-source selection 候选；seed-recheck 后该候选也未通过稳定性要求。
- 2026-05-23 第三次审稿建议进一步指出 test-set overfitting、full-conflict 监督泄漏、AUC 偶然性和 high-confidence error 稀疏性风险。该意见合理，全部采纳；因此先完成 gate，再根据结果决定是否实现新方法。
- 2026-05-23 最新审稿建议继续采纳：统一 fusion uncertainty 方向；gate 拆成 signal gate 和 selector behavior gate；组合分数第一版使用 z-score 等权无监督组合；若 CLIP-only 不显著，叙事降级为 multimodal disagreement / reliability-aware selection。
- 2026-05-23 最后收口：两层 gate 顺序定义为 pre-method signal gate -> minimal/offline selector behavior gate -> test confirmatory -> post-implementation mechanism gate；正式弱域由 train/val baseline bottom-k 决定；confidence 负对照拆为 confidence-uncertainty 和 overconfidence-only。
- 2026-05-23 实际 gate 结果显示：CLIP-only 不强，full conflict 有效但 confidence-uncertainty / fusion uncertainty 更强。因此不能强写 cross-modal conflict causality，应转为 reliability-aware multimodal disagreement selection。

本文档不包含代码修改。若后续读取源码、确认实现、查看 diff 或修改代码，必须登录远端活代码仓库：

```bash
ssh panda-autodl
cd /root/autodl-tmp/panda_repro/panda
```

本地 `remote_panda_work/` 只作为远端日志、代码片段和实验结果的证据副本，不能视为最新活代码仓库。

## PRCV/CCF-C 口径判断

PRCV 方向适配度高于 CVPR/ICCV 等顶会口径。原因是本项目更偏模式识别、多媒体理解、内容安全和应用型可靠性评估，而不是通用视觉基础模型或大规模视觉表示学习。

当前 PRCV 口径下的方案评估：

| 方案 | PRCV 适配度 | 中稿潜力 | 主要疑虑 |
| --- | --- | --- | --- |
| A Stable-Calibrated PANDA | 中 | Borderline | deterministic eval 和 threshold calibration 容易被认为是后处理 |
| B Fuzzy-Memory PANDA | 中 | Borderline+ | fuzzy domain / memory bank 已有相关工作，需要证明不是简单拼接 |
| C Ambiguity-Aware PANDA | 中 | 已降级 | CLIP-only 不强，不能主打图文冲突因果 |
| D Retrieval-PANDA | 中低 | 风险高 | 工程成本大，可复现性和证据质量难讲清 |
| Reliability-aware Disagreement PANDA | 高 | No-Go for current selector implementation | selector v2 clean branch/fusion variants 未过 deterministic |
| Uncertainty-aware Stable-source Selection | 中 | No-Go for current stable-source selector / 诊断保留 | seed42 过线但 seed2024 失败，三 seed val 均值低于 deterministic |
| R3-PANDA Regret Router | 中 | No-Go for current R3 v0 | self-domain route collapse，正向 variants 未过 deterministic |
| R4-PANDA Non-self Source-domain Intervention Consistency | 中 | No-Go for current D2 PAD-top2 forced-view | frozen-view validity 被 shuffled/bottom/random controls 打穿 |
| Boundary-sensitive DCA / Source-view Risk | 中 | No-Go for current D2 late DCA/source-view probe | PAD-ranked source prompt 没有打过 shuffled/random/bottom controls |
| Feature-aware PAD / Prototype Refinement | 中 | No-Go for current D2 hard ranking probe | feature ranking 被 shuffled/random/bottom controls 打穿 |
| Domain-conditioned Expert Gate | 中低 | Blocked/current checkpoint unsupported | 当前 checkpoint 不是 9-domain gate，只能作为 code-path caveat |
| Evidential / Reliability Extension | 中 | No-Go for current D4+D5 reliability selector / 诊断保留 | 三 seed val mean 低于 deterministic，seed2024 为强负例 |
| Reliability/uncertainty diagnostic + selector stability analysis | 中 | 证据池 / fallback | 不是当前主线；只服务于方法动机、强对照和失败边界分析 |
| Round 2 方法候选池：P2-A/P2-B/P2-C/P2-D | 中 | 已完成 / 无 Primary-Candidate | P2-A/P2-B/P2-C/P2-D 为当前 D3 offline/frozen 变体结论；P2-B final+aux residual 仅 Feasible-B 弱信号 |
| Round 3 Branch-Boundary Residual | 归档 | No-Go for current D3 offline residual | best primary 低于 original，并被 weighted-average ordinary combiner control 打穿 |
| Round 4 First-Principle Boundary Rebuild | 归档 | No-Go for current D3 offline patches / Diagnostic-only | R4-A/R4-D/R4-C 低于 original，R4-B 仅作 domain shortcut 诊断 |
| Round 5 Branch-Evidential Boundary Rebuilding | 高 | Gate-0 与 R5-A smoke 已完成 / No-Go for current R5-A implementation | G0-A 只支持 image-branch/final gradient conflict candidate signal；R5-A primary 低于 deterministic 且被 `aux_weight_2p0` control 打穿；R5 reserve/组合未被永久排除 |

PRCV 2026 常规投稿按公开 CFP 已经过期。除非已有投稿，本项目应按 PRCV 同档会议或下一届 PRCV 进行规划。

## 当前复现诊断

已完成 PANDA 在 Weibo-21 和 Weibo 上的三 seed 复现：

| Dataset | Macro-F1 | Accuracy | AUC |
| --- | ---: | ---: | ---: |
| Weibo-21 | 0.9474 ± 0.0073 | 0.9474 ± 0.0073 | 0.9879 ± 0.0014 |
| Weibo | 0.9415 ± 0.0034 | 0.9415 ± 0.0034 | 0.9866 ± 0.0011 |

基于现有 test predictions 的快速诊断：

说明：这部分只用于复现阶段后的问题发现和风险定位，不能作为正式方法设计或 gate 通过依据。正式论文中的 gate 必须以 train/val 为主，test 只做最终确认。

| Dataset | 弱域 | 主要现象 |
| --- | --- | --- |
| Weibo-21 | 科技、医药健康、社会生活 | 平均 per-domain Macro-F1 约 0.91-0.92，明显低于强域 |
| Weibo | 政治、科学、军事 | 平均 per-domain Macro-F1 约 0.83-0.85，错误更集中 |

阈值相关诊断：

- 使用 `abs(score - 0.5) <= 0.1` 作为阈值附近样本，比例约 1.5%-2.6%。
- 整体错误率约 4.5%-6.2%。
- 高置信错误样本比例约 1.5%-2.5%。

结论：

- 错误不是主要来自 0.5 阈值附近的边界样本。
- 单纯 threshold calibration 不能作为主贡献。
- 真正问题更像是领域相关高置信错判、跨域负迁移、模型内多模态分歧、融合不确定性，以及 Gumbel neighbor selection 的不稳定。
- “图文冲突导致迁移不可靠”已经被 gate 降级：CLIP-only 不强，不能作为主因果证据。当前应把 CLIP dissimilarity 作为辅助特征和消融项，把 branch disagreement / fusion uncertainty 作为 reliability-aware selection 的核心信号。

## 投稿前生死门

历史路线说明：在实现 Reliability-aware Disagreement PANDA 前，必须先执行并复核 `CS-PANDA投稿前生死门诊断方案.md` 中定义的 gate。该 gate 已完成，结论先是放弃强 CLIP 图文冲突因果线，改走 reliability-aware multimodal disagreement selection；随后 selector v2 与 seed-recheck 继续显示该方法线未形成稳定性能闭环。因此当前不再按该主线投稿，只保留为 failed selector hypothesis 和 diagnostic evidence。

### 实际 Gate 结果摘要

已完成两数据集、三 seed、train/val/test 扩展诊断导出和 gate 分析。

| Split | Dataset | CLIP-only AUC | Full conflict AUC | Confidence-uncertainty AUC | Fusion uncertainty AUC |
| --- | --- | ---: | ---: | ---: | ---: |
| val | Weibo | 0.5087 | 0.7463 | 0.8589 | 0.8559 |
| val | Weibo-21 | 0.5314 | 0.8515 | 0.8768 | 0.8645 |
| test | Weibo | 0.4748 | 0.8007 | 0.8933 | 0.8769 |
| test | Weibo-21 | 0.5572 | 0.8200 | 0.9013 | 0.8752 |

Val-based 弱域：

- Weibo：国际、经济、教育。
- Weibo-21：灾难事故、科技、医药健康。

Val-selected offline lambda：

- Weibo：0.0，未发现 lambda 改善 val selector behavior。
- Weibo-21：0.05，最小 lambda 改善 high-disagreement vs low-disagreement Jaccard change gap。

Gate 结论：

- 不通过强图文冲突叙事。
- 通过 reliability / uncertainty / multimodal disagreement 叙事。
- Weibo 的 offline selector behavior 不支持强 re-ranking 机制；Weibo-21 有一定 selector 行为证据。

已验证结论：

1. CLIP-only 不能稳定区分 error vs correct，强图文冲突因果线不通过。
2. Branch disagreement、fusion uncertainty 与 confidence-uncertainty 对错误和高置信错误有显著区分力。
3. Full conflict 有效，但没有超过 confidence-uncertainty / fusion uncertainty，因此不能把方法写成“复杂冲突机制优于不确定性”。
4. Random control 不显著，overconfidence-only 对 high-confidence error 富集不成立。
5. Weibo-21 的 offline selector 行为有弱机制苗头；Weibo 没有 re-ranking 收益。

后续通过线：

- 新方法必须赢过或至少区别于 deterministic selector、confidence-uncertainty-only、fusion-only、branch-only、CLIP-only、overconfidence-only 和 random control。
- 至少一个数据集 Macro-F1/Acc 稳定提升 >=0.5 个百分点，另一个数据集不退化。
- High-confidence error rate、ECE/Brier、弱域 F1、prediction-level repeated-forward variance 至少两个指标改善。
- 若只提升 0.1-0.2 个百分点，必须有很强 selector 机制证据；否则按 PRCV/同档口径仍偏危险。

如果后续方法不通过：

- 不按 Reliability-aware Disagreement PANDA 主线投稿。
- 改写为 PANDA reproduced + reliability diagnostic + baseline study，或转向 leave-one-domain 泛化。
- 不能硬把 reliability-aware selector 写成核心贡献。

红线：

- 不能用 test label 调 reliability/disagreement 权重、建 prototype 或选择方法。
- Reliability/disagreement score 不能用 `is_error` 监督训练，否则会变成错误检测器。
- Per-domain 相关性只能作为辅助图，不能作为唯一 gate。
- 在查看 test confirmatory 结果前，必须先固定 gate 配置，包括 reliability/disagreement score 定义、组合权重搜索空间、通过阈值、bootstrap/permutation 设置和统计检验方案。
- 若 reliability/disagreement 组合权重需要调参，只能在 train/val 上完成，并保存 val-selected 权重；test 不能参与任何选择。
- 组合分数第一版默认使用 z-score 后等权无监督组合。Val 调权只作为附录或消融，不作为主结果。
- Gate 必须分两层：先证明 reliability/disagreement signal 与错误/高置信错误相关，再证明 selector 行为确实改变。
- 第一层是 pre-method signal gate，不需要实现新 selector；第二层先用导出的 PAD/neighbor logits 做 minimal/offline selector behavior gate，通过后再做最小方法实现与 post-implementation mechanism gate。
- 正式弱域必须由 train/val baseline 的 bottom-k domain F1 或 top-k domain error rate 确定，test 只验证这些域是否仍弱。
- Confidence 负对照拆成 `confidence-uncertainty = 1 - max(y_score, 1-y_score)` 和 `overconfidence-only = max(y_score, 1-y_score)`。

## 最优论文主线

原建议论文题目：

**Conflict-aware Stable Neighbor-Domain Adaptation for Multimodal Fake News Detection**

Gate 后曾更稳题目：

**Reliability-aware Multimodal Disagreement Selection for Multimodal Fake News Detection**

Selector v2 Go/No-Go 后一度出现的候选题目：

**Uncertainty-aware Stable Source Selection for Multimodal Fake News Detection**

中文主线：

多模态假新闻检测中，PANDA 的错误更明显地与模型可靠性和不确定性相关，而不是与独立 CLIP 图文不一致强相关。selector v2 进一步显示，clean branch/fusion disagreement 不能形成主方法闭环；seed-recheck 又显示 uncertainty-aware stable-source 配方不稳定。因此当前更可信的方向是诊断可靠性/不确定性如何影响错误、弱域和邻域选择，而不是宣称一个已稳定有效的新 selector。

英文主线：

Reliable multimodal fake news detection should consider not only domain similarity but also sample-level uncertainty, source-domain stability, and whether these signals enter the final classifier boundary. After selector-level validation and seed recheck, the current evidence rules out the old stable-source selector as a main method, but supports using reliability/uncertainty diagnostics and failed-selector boundary analysis as evidence for the next method candidates.

## 方法设计

### 模块 1：Lightweight Reliability / Disagreement Modeling

目标：

为每个样本构造轻量可靠性/多模态分歧表征，不引入大规模外部知识或不可控 LLM。

推荐特征：

| 特征 | 定义 | 作用 |
| --- | --- | --- |
| Branch disagreement | `abs(p_text - p_image)` | 衡量文本分支与图像分支预测分歧 |
| Fusion uncertainty | entropy 或 `1 - abs(2 * p_fusion - 1)` | 衡量融合分支不确定性，数值越大越不确定 |
| CLIP dissimilarity | `1 - cos(clip_text, clip_image)` | 辅助图文语义不一致特征，仅作消融与补充 |
| Reliability embedding | MLP 或线性层处理上述轻量特征 | 得到可学习可靠性/分歧表示 |

实现原则：

- 优先复用 PANDA 已有的 CN-CLIP、text/image/fusion 辅助预测。
- 不替换 backbone。
- 不引入外部检索或 LLM，保持可复现。
- `p_text`、`p_image`、`p_fusion` 参与 reliability feature 时默认使用 detach 版本，避免模型通过自反馈捷径优化 selector。
- Branch disagreement 和 fusion uncertainty 属于模型内可靠性信号，不能包装成“图文冲突”因果证据；CLIP-only 和随机/置信度负对照必须同时报告。
- `abs(p_fusion - 0.5)` 方向相反，数值越大越高置信，不能作为 uncertainty 定义。
- 由于 CLIP-only 已不显著，正式写作使用 multimodal disagreement / reliability-aware selection，不强写 cross-modal conflict 因果。

### 模块 2：Reliability-aware Neighbor Selection

PANDA 原始邻域选择主要基于 PAD：

```text
sim_domain(s, t) = 1 / (PAD(s -> t) + eps)
```

改进思路：

为每个领域维护 reliability/disagreement prototype，表示该领域典型的模型内多模态分歧和不确定性模式。prototype 必须由 train split pre-fit、每个 epoch 开头 pre-epoch fit，或 EMA momentum 0.9/0.99 得到；不得使用 test 或 error label。

第一版 `abs(score - domain_mean)` 已在 seed42 sanity 中暴露问题：`confidence_uncertainty` 与 `overconfidence = 1 - confidence_uncertainty` 会在绝对距离上数学等价。普通 signed z-score product 也仍会等价，因为 `z_over = -z_unc` 后乘积不变：

```text
z_over_sample * z_over_domain
= (-z_unc_sample) * (-z_unc_domain)
= z_unc_sample * z_unc_domain
```

因此下一版不能只换成 signed product，必须采用 asymmetric / directional gating。例如：

```text
penalty_high_unc(i, s) = max(0, z_unc_i) * max(0, z_unc_s)
logit(i, s) = log sim_domain(s, t_i) - lambda * penalty_high_unc(i, s)
```

或奖励高不确定样本选择更稳定 source domain：

```text
reward_stable_source(i, s) = max(0, z_unc_i) * max(0, -z_unc_s)
logit(i, s) = log sim_domain(s, t_i) + lambda * reward_stable_source(i, s)
```

然后在该 logit 上执行 Gumbel top-k 或 deterministic top-k。

预期效果：

- 避免只因为 domain prototype 接近就迁移不可靠的邻域知识。
- 对高分歧/高不确定样本，优先选择更可靠或分歧模式更匹配的邻域。
- 让 neighbor selection 更可解释，可画 domain-to-neighbor heatmap 和 disagreement-conditioned selection heatmap。

### 模块 3：Stable Neighbor-Domain Selection

训练阶段：

- 保留 Gumbel top-k 以维持探索。
- 在 reliability-aware logits 上采样邻域。
- 加入轻量稳定性正则，例如 selection margin 或 consistency loss。
- 必须先把稳定性底座与 reliability selector 拆开：PANDA Gumbel train/eval、Gumbel train + deterministic eval、deterministic train/eval、selection margin、consistency regularization。

验证/测试阶段：

- 默认使用 deterministic top-k，避免 eval 随机性污染指标。
- 可补充 MC-Gumbel voting 作为稳定性对照。

推荐稳定性损失：

```text
L_stab = max(0, margin - (logit_top1 - logit_top2))
```

或：

```text
L_cons = KL(selector(x, noise1) || selector(x, noise2))
```

优先实现 margin loss，因为更简单、可控、易消融。

### 模块 4：Reliability Calibration as Analysis

Calibration 不作为核心方法贡献，只作为可靠性分析和辅助模块。

保留内容：

- Global threshold calibration。
- Per-domain threshold calibration。
- ECE。
- Brier score。
- Repeated eval variance。

写作定位：

- Calibration 用来解释“为什么 AUC 高而 F1/Acc 不完全同步”。
- 如果 calibration 有提升，放入可靠性分析或附录。
- 主贡献是 reliability-aware neighbor selection 和 stable selection；calibration 只用于分析和辅助对照。

## 损失函数建议

总损失：

```text
L = L_cls + alpha * L_aux + beta * L_rec + gamma * L_stab + eta * L_rel
```

其中：

| 损失 | 说明 |
| --- | --- |
| `L_cls` | 主分类 BCE |
| `L_aux` | text/image/fusion 辅助分类损失，沿用 PANDA |
| `L_rec` | prototype reconstruction loss，沿用 PANDA |
| `L_stab` | neighbor selection 稳定性约束 |
| `L_rel` | 可选 reliability/disagreement representation regularization |

第一版建议：

- 先实现 `L_stab`。
- 暂不强行加复杂 `L_rel`，避免超参过多。
- reliability/disagreement prototype 可用 batch/domain EMA 或训练集统计初始化。
- 第一版不加复杂 `L_rel`。先做 branch disagreement + fusion uncertainty -> reliability prototype -> 调制 GNS logits -> `L_stab`，把贡献链条保持干净。
- Prototype 和组合权重只能使用 train/val。test 只做最终确认。
- 第一版优先采用固定定义或 z-score 后等权组合，不用 `is_error` / `is_high_conf_error` 监督 MLP。
- 如果后续使用可学习 reliability embedding，训练目标应来自分类主任务、邻域选择或自监督一致性，而不是错误标签监督。
- Val-only 调权只作为附录或消融，避免被认为在 val 上学习错误检测分数。

## 实验设计

### Selector v2 Go/No-Go 小网格

在正式两数据集三 seed 新方法实验前，先执行 Weibo-21 seed42 5-epoch selector v2 小网格。该阶段只用于 val-only 路线判断，不作为正式主表结果。

2026-05-24 已完成结果：

- 34/34 val/test exports 全部完成；远端无残留训练/评估进程，无 traceback、OOM 或 missing checkpoint 等真实错误。
- `deterministic_eval_l0` val F1/Acc/AUC 为 `0.939835/0.939837/0.981206`。
- 所有 branch_fusion/fusion clean variants 的 val F1/Acc 都低于 deterministic，因此 clean Reliability-aware Disagreement selector 是 No-Go。
- 唯一过线 variant 是 `confidence_uncertainty + stable_source_reward + pre_epoch + lambda=0.2`，val F1/Acc/AUC 为 `0.941395/0.941463/0.984960`。
- 该结果不能包装成 branch/fusion disagreement 主机制；它只支持 uncertainty-aware stable-source selection 候选路线。
- 随后 seeds 2024/2026 复核显示该候选不稳定：seed2024 失败，合并三 seed val F1/Acc mean `0.936018/0.936043`，低于 deterministic `0.937093/0.937127`。

必须比较：

- `panda_gumbel`
- `deterministic_eval`
- `deterministic_train`
- `deterministic_train + boundary_margin`
- `pre_epoch + high_unc_penalty`
- `pre_epoch + stable_source_reward`

约束：

- Reliability signal 主判断优先使用 branch_fusion / fusion，不把 CLIP 混入 clean mechanism。
- Confidence-uncertainty、overconfidence-only、random 必须作为 control。
- Lambda 网格先固定为 `[0.05, 0.1, 0.2]`，最多补 `0.5`；不得根据 test 结果追加 lambda 或改公式。
- 通过线：val F1/Acc 不低于 deterministic，同时 AUC、ECE、Brier、high-confidence error、弱域 F1 中至少两个指标更好；若已补 prediction-level repeated-forward 导出，则 prediction variance 也计入通过指标。

决策分岔：

- 已执行结论：`deterministic_train + boundary_margin` 未过线，不能作为当前主线。
- 已执行结论：clean branch/fusion directional reliability 未过线，不能继续作为 Reliability-aware Disagreement PANDA 主线。
- 已执行结论：`confidence_uncertainty + stable_source_reward + pre_epoch + lambda=0.2` 的 seed 稳定性复核未通过；该线降级为 reliability/uncertainty 证据和失败消融，不作为论文主线。Round 2 方法候选赛马随后也已完成且无 `Primary-Candidate`，Round 3 Branch-Boundary Residual、Round 4 First-Principle Boundary Rebuild、Round 5 Gate-0 与 R5-A 单项 smoke 也已完成；R5-A 已 `No-Go`，当前没有 Round 5 `Primary-Candidate`。

### 主表

必须包含：

| Method | Weibo-21 F1 | Weibo-21 Acc | Weibo-21 AUC | Weibo F1 | Weibo Acc | Weibo AUC |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| MMDFND reproduced | 0.9262 ± 0.0147 | 0.9263 ± 0.0147 | 0.9676 ± 0.0114 | 0.9094 ± 0.0243 | 0.9094 ± 0.0243 | 0.9719 ± 0.0089 |
| DAMMFND reproduced | 0.9436 ± 0.0075 | 0.9436 ± 0.0075 | 0.9839 ± 0.0049 | 0.9374 ± 0.0028 | 0.9374 ± 0.0028 | 0.9856 ± 0.0012 |
| PANDA reproduced | 0.9474 ± 0.0073 | 0.9474 ± 0.0073 | 0.9879 ± 0.0014 | 0.9415 ± 0.0034 | 0.9415 ± 0.0034 | 0.9866 ± 0.0011 |
| Uncertainty-aware Stable-source Selection | No-Go，seed-recheck 未通过 | No-Go，seed-recheck 未通过 | No-Go，seed-recheck 未通过 | 未解锁 | 未解锁 | 未解锁 |
| Round 3 Branch-Boundary Residual | 待 gate | 待 gate | 待 gate | 未解锁 | 未解锁 | 未解锁 |

要求：

- Weibo-21 和 Weibo 都跑。
- seeds 42 / 2024 / 2026。
- 统一使用独立重算指标。
- 报告 mean ± sample std。
- Clean Reliability-aware Disagreement PANDA 没有通过 Weibo-21 seed42 selector v2 Go/No-Go，不能启动两数据集三 seed正式主表。
- Winning control 在 Weibo-21 seeds 2024/2026 复核后未稳定通过，也不能以 uncertainty-aware stable-source selection 名义规划正式主表。

### 消融实验

| Variant | Reliability-aware | Deterministic eval | Stability regularization | Calibration | 目的 |
| --- | --- | --- | --- | --- | --- |
| PANDA reproduced | No | No | No | No | 原始基线 |
| + deterministic selector | No | Yes | No | No | 强对照：验证提升是否只是去掉 eval 随机性 |
| + branch-only disagreement | branch only, detach | Yes | No | No | 验证模型分支分歧信号 |
| + fusion-uncertainty-only | uncertainty only, detach | Yes | No | No | 验证是否只是融合不确定性包装 |
| + CLIP-only auxiliary | CLIP only | Yes | No | No | 验证独立图文冲突信号是否有辅助价值 |
| + confidence-uncertainty control | `1 - max(y_score, 1-y_score)` | Yes | No | No | 强负对照：验证方法不只是 uncertainty gating |
| + overconfidence-only control | `max(y_score, 1-y_score)` | Yes | No | No | 反证：高置信错误不能只由过度自信解释 |
| + random control | random/shuffled | Yes | No | No | 反证：不能只赢在噪声正则 |
| + full reliability-aware selector | Yes | Yes | No | No | 验证可靠性感知邻域选择 |
| + stability regularization | Yes | Yes | Yes | No | 验证训练稳定性 |
| + calibration | Yes | Yes | Yes | Yes | 可靠性辅助，不作为主贡献 |

### 分析图

必须准备：

- Per-domain F1/Acc/AUC bar chart。
- Domain-to-neighbor heatmap。
- Disagreement-conditioned neighbor selection heatmap。
- High-disagreement vs low-disagreement selected-neighbor Jaccard change。
- Selection entropy / repeated eval selection frequency 表。
- PAD/neighbor logits topS-top(S+1) boundary margin 分析；PANDA 选 top-2，因此 Weibo-21 当前重点是 top2-top3。
- 错误样本的 reliability/disagreement score 分布。
- 高置信错误样本案例表。
- Repeated eval variance 曲线或表格。

### 可靠性指标

| 指标 | 用途 |
| --- | --- |
| ECE | 衡量概率校准 |
| Brier score | 衡量概率预测质量 |
| Repeated eval variance | 衡量 Gumbel selector 随机性；selector entropy/frequency 与 prediction-level `y_score` variance 均已补齐，后者显示 Gumbel 有非零预测方差，deterministic / winning-control 近零 |
| Best-worst seed gap | 衡量跨 seed 稳定性 |
| High-confidence error rate | 衡量高置信错判风险 |

### 显著性与稳定性

最低要求：

- 每个 seed 都报告 delta。
- 至少两个数据集之一每 seed 同向提升。
- 如果提升幅度接近，补 paired bootstrap 或 Wilcoxon signed-rank test。
- Gate 和主结果优先报告 domain-stratified bootstrap 或 seed-aware bootstrap；单纯 sample bootstrap 只能作辅助。
- 若未来重新设计新方法，投稿最低可接受结果形态仍是：至少在一个数据集上 Macro-F1/Acc 稳定提升 0.5 个百分点以上，另一个数据集不退化；同时 high-confidence error rate、ECE/Brier、prediction-level repeated-forward variance、弱域 F1 四类指标至少两个明显改善。当前已跑 selector 方案均未达到该要求。
- 如果只提升 0.1-0.2 个百分点，按 PRCV/同档会议口径仍然危险，必须依靠强机制证据或转向分析型论文。

## 必须补的实验

已完成 P0：

0. 导出 train/val/test 扩展 predictions，并在 val 上执行投稿前 gate，test 只做最终确认。
1. 在查看 test confirmatory 结果前固定 `conflict_gate_config.yaml` 和 val-selected 权重。
2. 用 train/val baseline bottom-k domain F1 或 top-k error rate 固定正式弱域。
3. 执行第一层 pre-method signal gate。
4. 基于导出的 PAD/neighbor logits 执行第二层 minimal/offline selector behavior gate。
5. Test 只做 confirmatory analysis。
6. 实跑 MMDFND Weibo-21 / Weibo 三 seed。
7. 实跑 DAMMFND Weibo-21 / Weibo 三 seed。
8. 对现有 PANDA predictions 生成 per-domain/error/reliability 诊断表。

P1：

1. 在远端 PANDA 活代码仓库新建 innovation 分支或复制实验目录。
2. 实现 deterministic eval selector，作为强对照。
3. 实现 detach 后的 branch disagreement + fusion uncertainty feature extraction。
4. 拆开 deterministic/stability 底座：PANDA Gumbel train/eval、Gumbel train + deterministic eval、deterministic train/eval、selection margin、consistency regularization。
5. 将 reliability/disagreement prototype 改为 train pre-fit、pre-epoch fit 或 EMA。
6. 实现 asymmetric / directional reliability-aware GNS，不能只用 signed product。
7. 实现 CLIP-only、confidence-uncertainty-only、fusion-only、branch-only、overconfidence-only、random control。
8. 实现 selection logging。
9. 补 prediction-level repeated-forward `y_score` variance export。已完成，作为稳定性诊断而非方法通过证据。
10. 跑 Weibo-21 seed 42 sanity 和单 seed 快速消融。

P2：

1. 完整跑 Weibo-21 三 seed。
2. 完整跑 Weibo 三 seed。
3. 跑消融和可靠性分析。
4. 生成论文图表。

## 写作结构

### Introduction

核心句：

现有多领域多模态假新闻检测方法通常根据领域相似性进行知识迁移，但领域相似并不等价于迁移可靠；当目标样本存在较高多模态分支分歧和融合不确定性时，邻域选择更容易出现不稳定迁移和高置信错判。

贡献：

1. We reproduce PANDA, MMDFND, and DAMMFND under a three-seed protocol and identify reliability-related high-confidence errors in PANDA.
2. We show that independent CLIP-based image-text conflict is not sufficient, while branch disagreement and fusion uncertainty provide stronger reliability signals.
3. We evaluate reliability-aware multimodal disagreement selection and find it does not pass the selector v2 Go/No-Go gate under clean branch/fusion signals.
4. We show that the seed42-positive uncertainty-aware stable-source control does not pass seed stability recheck, so it should be reported as a boundary condition rather than a method contribution.
5. We provide per-domain, reliability, selector-behavior, and repeated-evaluation analyses on Weibo-21 and Weibo; R4-PANDA and Round 2 are retained as failed/boundary-condition evidence, while the current method candidate is Round 3 Branch-Boundary Residual.

### Method

建议结构：

1. PANDA backbone recap。
2. Reliability / uncertainty diagnostic protocol。
3. Selector stability and failed-hypothesis gates。
4. Boundary conditions of reliability-aware neighbor-domain selection。
5. Optional R4 candidate protocol：non-self source-domain intervention validity gate，不作为已完成方法结果。

### Experiments

建议结构：

1. Datasets and baselines。
2. Implementation details。
3. Main results。
4. Ablation study。
5. Per-domain analysis。
6. Reliability and stability analysis。
7. Case study。

## 风险与止损

### 风险一：Reliability-aware selector 提升不足

止损：

- 先检查 reliability/disagreement score 是否能区分错误样本和正确样本。
- 若不能，缩减为 deterministic selector + 稳定性/可靠性分析，不硬做复杂 selector。
- 若提升不足，转为以稳定性和可靠性诊断为主，减少指标提升承诺。
- 若新方法只等价于 confidence-uncertainty-only 或 fusion-only control，则不能作为主贡献。
- 下一版 reliability selector 必须在 val 上 F1/Acc 不低于 deterministic，同时 AUC、ECE、Brier、high-confidence error、弱域 F1 中至少两个指标更好；若已补 prediction-level repeated-forward 导出，则 prediction variance 也计入通过指标。

### 风险一补充：Test-set 过拟合嫌疑

止损：

- Gate 主要在 val 上完成，test 只做 confirmatory analysis。
- 方法定义、组合权重、prototype、阈值、超参和消融顺序都不能由 test label 决定。
- 论文写作中明确说明 gate 在 train/val 上建立，test 只报告最终确认结果。
- 如果 test confirmation 与 val gate 不一致，只能如实报告不一致，不反向修改 reliability/disagreement 定义。

### 风险一补充：Reliability score 被认为是自反馈

止损：

- Branch disagreement 和 fusion uncertainty 均使用 detach。
- 消融必须包含 CLIP-only、branch-only、fusion-only、full reliability-aware、confidence-uncertainty、overconfidence-only、random control。
- 消融必须把 confidence 拆成 confidence-uncertainty 和 overconfidence-only。
- Overconfidence control 必须在数学上与 confidence-uncertainty control 不等价；不能使用 `abs(score - domain_mean)` 或普通 signed product 作为唯一调制。
- 若 full reliability-aware selector 的优势主要来自 confidence-uncertainty，则不能主张新 selector 有独立贡献。

### 风险二：方法被认为只是 uncertainty gating

止损：

- 不把 uncertainty score 直接拼到最终分类器作为唯一改动。
- 必须让 reliability/disagreement score 作用于 neighbor selection。
- 必须与 confidence-uncertainty-only、fusion-only 和 random control 做干净对照。
- 用 neighbor heatmap 证明选择机制变了。

### 风险三：Baseline 实跑结果不稳定

止损：

- 统一运行协议、seeds、数据 split 和指标脚本。
- reported baseline 只放参考，主表以 reproduced baseline 为准。
- 透明记录失败或差异。

### 风险四：PRCV 2026 时间已过

止损：

- 当前按 PRCV 同档会议或下一届 PRCV 规划。
- 方法和实验标准不绑定单一会议。

### 风险五：泛化表述过大

止损：

- 只主张 Chinese multimodal multi-domain fake news detection 或 Chinese/social-media setting。
- 不泛化到 general multimodal misinformation detection。
- 若时间允许，补 FineFake 或 leave-one-domain 泛化；若不补，在标题、摘要和结论中收敛表述。

## 最终建议

当前最稳证据底座已从 **Conflict-aware Stable Neighbor-Domain Adaptation** 降级为 reliability/uncertainty 与 selector/source-view/domain-gate/branch-boundary/Round4/Round5 边界证据，但论文主线不能停在诊断型报告。源码审计后，方法性论文路线曾继续走 Round 5 `Branch-Evidential Boundary Rebuilding` 候选池；Gate-0 深度复盘只让 R5-Prime / R5-A+D / R5-S 保持 `Not-Unlocked`，并未直接 D4 训练验证这些组合。随后 R5-A 单项 image-branch/final gradient consistency smoke 因低于 deterministic 且被 aux weight control 打穿而 `No-Go for current r5a_image_project_l1p0 training implementation`。当前没有可进入三 seed val 复核的 Round 5 候选；若继续方法探索，必须提出本质不同的新候选并重新预注册 Gate-0。

不要把论文写成：

```text
复现 PANDA 后做 deterministic selector 和 threshold calibration。
```

要写成：

```text
多模态假新闻检测中，领域迁移是否可靠不仅取决于领域原型相似性，也取决于样本级不确定性、源域稳定性，以及这些信号是否真正进入最终分类边界。当前不能强写 branch/fusion disagreement 主机制，也不能把 seed-sensitive 的 uncertainty-aware stable-source selector、aux-logit residual 或 Round4 离线 boundary correction 写成稳定方法；下一轮应验证 PANDA 的剩余错误是否来自训练动力学问题，例如 branch-final gradient conflict、modality reliance instability 或 label-preserving domain nuisance，并证明收益不是普通 dropout、PCGrad、DG 正则、calibration、stacking 或 kNN 后处理。
```

诊断线只作为证据池和 fallback；真正要冲 PRCV/同档方法论文，必须继续快速赛马 Round 5 候选，并用现有 No-Go 证据证明新主线不是旧 selector、普通 calibration、ordinary stacking、kNN 后处理、普通 DG 正则或 uncertainty 包装。
