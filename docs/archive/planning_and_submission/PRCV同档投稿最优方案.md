# PRCV 同档投稿最优方案

日期：2026-05-23

状态更新（2026-05-28）：2026-05-26 的 Round 5 口径已继续后移。Round 6/7 当前作用域验证已闭环且没有 `Primary-Candidate`；新的待执行规划入口已切到 Round 7 `Risk-Aware Final-Boundary Learning`，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md`、`round7_candidate_registry.md`、`round7_gate0_manifest_TEMPLATE.json` 和 `todo.md`。本文档以下投稿判断只作为历史风险记录。

状态更新（2026-05-26）：本文档的早期 R4 / Track A-B 口径、Round 2 方法候选池、Round 3 Branch-Boundary Residual 以及 Round 4 First-Principle Boundary Rebuild 均已完成归档。Round 5 training-dynamics Gate-0 与 R5-A 单项 seed42 smoke 也已完成：G0-E/G0-S No-Go，G0-D 仅为 destructive boundary fragility，G0-A 只保留 image-branch/final gradient conflict candidate signal；R5-A primary 低于 deterministic 且被 `aux_weight_2p0` control 打穿。当前仍不是诊断型报告收尾，但没有 `Primary-Candidate`，不复核 seeds、不扩 Weibo、不看 test。以下早期内容仅作为历史投稿判断和风险记录。

## 结论

2026-05-26 最新更新：R3-PANDA Regret Router、历史 R4-PANDA frozen forced-view validity、P0-B DCA/source-view sensitivity、P1-A feature-aware PAD、P1-B domain-conditioned expert gate audit、P1-C evidential/reliability extension、Round 2 P2-A/P2-B/P2-C/P2-D、Round 3 Branch-Boundary Residual、Round 4 First-Principle Boundary Rebuild、Round 5 Gate-0 以及 R5-A 单项 smoke 均已完成。当前没有 `Primary-Candidate`；若继续方法论文，必须提出本质不同的新候选并重新预注册 Gate-0。

Round 2 结论：P2-A、P2-C、P2-D No-Go；P2-B reliability adapter No-Go；P2-B 无 reliability `final+aux logits` residual adapter 曾保留为 `Feasible-B` 弱边界信号。Round 3 已围绕该弱信号完成强对照复核并 No-Go，因此不再沿 aux-logit / branch-boundary residual 续参。

2026-05-25 已新增 `创新方案赛马总控与实施协议.md`。投稿方法线不由单一候选预设胜出，而按候选池赛马推进。任何方案先过 gate 只标记 `Feasible-A/B`，待所有候选赛完后再确定最终主线。

按 PRCV/CCF-C 口径，本项目原先最优方向是：

**Reliability-aware Multimodal Disagreement Selection for Multimodal Fake News Detection**

即：在 PANDA 的原型邻域迁移框架上，引入样本级多模态分支分歧与融合不确定性来调制 neighbor-domain selection，并使用 deterministic selector 或稳定化训练/推理降低 Gumbel selector 的随机波动。

但 2026-05-24 selector v2 5-epoch Go/No-Go 后，clean branch/fusion disagreement 主线未通过：所有 branch_fusion/fusion variants 的 val F1/Acc 都低于 deterministic。seed42 一度出现的候选方向是：

**Uncertainty-aware Stable Source Selection for Multimodal Fake News Detection**

即：正面承认唯一过线信号来自 confidence uncertainty，研究高不确定样本是否应选择更稳定的 source domain，而不是把该结果包装成 clean multimodal disagreement 机制。

随后 Weibo-21 seeds 2024/2026 seed-recheck 显示该候选也不稳定：seed2024 失败，三 seed val F1/Acc mean 低于 deterministic。因此旧 selector 线不建议以新方法主表投稿；这些证据只作为 Round 2 / Round 3 方法设计的动机和强对照。

原候选方向是：

**Conflict-aware Stable Neighbor-Domain Adaptation for Multimodal Fake News Detection**

2026-05-23 至 2026-05-24 gate 跑通后，强 CLIP 图文冲突证据不足；因此不再主打“图文语义冲突导致迁移失败”的因果叙事。

二次审稿人视角评估后，补充判断如下：

- 强 CS-PANDA / CLIP 冲突线已降级；selector v2 后 clean reliability-aware multimodal disagreement selection 未通过；winning control seed-recheck 后 uncertainty-aware stable-source selection 也未稳定通过。
- 投稿前 gate 已证明 branch disagreement、fusion uncertainty、confidence-uncertainty 与错误更相关，但也暴露出 uncertainty-gating 风险。
- 如果新方法只等价于 uncertainty gating，按当前故事投稿会回落到 Weak Reject 风险。
- Gate 必须主要在 val 上做，test 只作为最终确认，避免 test-set 过拟合嫌疑。
- 第三次审稿建议合理，应作为硬约束采纳：test label 不参与方法选择，reliability/disagreement score 不使用 `is_error` 监督，AUC/enrichment 必须带置信区间或显著性检验。
- 当前预期不是“稳中”，而是新方法实验扎实时达到 Borderline 到 Weak Accept。
- 最新收紧意见继续采纳：fusion uncertainty 统一为 entropy 或 `1 - abs(2p - 1)`；gate 拆成 signal gate 与 selector behavior gate；组合分数第一版采用 z-score 等权无监督组合。
- CLIP-only 不显著，不能强写“图文冲突导致错误”；branch/fusion v2 也未过线，正式写作不能再使用 clean multimodal disagreement 作为主机制。
- 两层 gate 顺序固定为：pre-method signal gate -> minimal/offline selector behavior gate -> test confirmatory -> post-implementation mechanism gate。后续方法训练应基于该 gate 结论启动。
- 正式弱域由 train/val baseline bottom-k domain F1 或 top-k error rate 确定，test 只确认。
- Confidence 负对照拆成 confidence-uncertainty 和 overconfidence-only。
- 实际 gate 结果：CLIP-only 不强；full conflict 有效但弱于 confidence-uncertainty / fusion uncertainty。因此后续必须证明新 selector 不是 confidence/fusion uncertainty 的包装。

## Gate 结果

| Split | Dataset | CLIP-only AUC | Full conflict AUC | Confidence-uncertainty AUC | Fusion uncertainty AUC |
| --- | --- | ---: | ---: | ---: | ---: |
| val | Weibo | 0.5087 | 0.7463 | 0.8589 | 0.8559 |
| val | Weibo-21 | 0.5314 | 0.8515 | 0.8768 | 0.8645 |
| test | Weibo | 0.4748 | 0.8007 | 0.8933 | 0.8769 |
| test | Weibo-21 | 0.5572 | 0.8200 | 0.9013 | 0.8752 |

解释：

- CLIP-only 没有提供足够独立图文冲突证据。
- Full conflict 对错误有区分力，但主要像 reliability / disagreement signal。
- Overconfidence-only 对 high-confidence error 不成立，说明不是单纯“越自信越错”。
- Weibo offline lambda 为 0.0，不能硬写该数据集上 selector re-ranking 有机制收益；Weibo-21 lambda 为 0.05，可作为机制分析的主要数据集。

## Venue 口径

PRCV 适配点：

- 模式识别与计算机视觉。
- 多模态融合与多媒体理解。
- 多媒体内容安全。
- 虚假内容、深度伪造、可信检测相关方向。
- 性能评测、可靠性与基准分析。

时间提醒：

- PRCV 2026 常规投稿公开口径已在 2026-04 中下旬截止。
- 当前日期为 2026-05-23，若没有已投稿稿件，应按 PRCV 同档会议或下一届 PRCV 规划。

参考来源：

- PRCV 2026 AC 学术平台页面：https://www.academicenter.com/conferences/details/PRCV2026.html
- 智源社区 PRCV 2026 征稿转发：https://hub.baai.ac.cn/view/54107
- PRCV 官网：https://www.prcv.cn/

## 审稿人视角判断

| 版本 | 优点 | 风险 | 结论 |
| --- | --- | --- | --- |
| Stable-Calibrated PANDA | 工程可行，直接回应复现发现 | 像后处理，创新偏弱 | 不建议单独主打 |
| Ambiguity-Aware PANDA | 多模态味道强，贴合 PRCV | 需要证明影响 neighbor selection | 建议主打 |
| Conflict-aware Stable PANDA | 兼顾多模态冲突和可靠迁移 | CLIP-only gate 未通过，强冲突叙事不足 | 不再作为强主线 |
| Reliability-aware Disagreement PANDA | 贴合早期 gate，强调可靠性、多模态分歧和稳定选择 | selector v2 clean branch/fusion 未过线 | No-Go，不作为当前主线 |
| Uncertainty-aware Stable-source Selection | seed42 过线结果来自 confidence uncertainty + stable source reward | seeds 2024/2026 复核后 seed2024 失败，三 seed val F1/Acc 均值低于 deterministic | No-Go，不作为正式方法 |
| R3-PANDA Regret Router | 试图把 prototype similarity 转为 supervised source utility | self-domain route collapse，正向 variants 未过 deterministic | No-Go for current R3 v0；全新 self-suppressed source mixture 需新验证 |
| R4-PANDA Non-self Source-domain Intervention Consistency | 避开 self-route collapse，直接训练 non-self source intervention 下的分类稳定性 | frozen-view validity 被 shuffled/bottom/random controls 打穿 | No-Go for current PAD-top2 forced-view；保留为当前变体失败边界 |
| Reliability/Uncertainty Diagnostic | 证据链完整，能解释错误、弱域、可靠性和 selector 失败边界 | 不是强方法贡献，投稿定位偏分析/复现诊断 | 证据池 / fallback，不是当前主线 |
| Round 2 final-boundary method pool | 直接测试 final-boundary correction、boundary adapter、真实 domain expert 和 source-utility reorganization | P2-A/P2-C/P2-D No-Go；P2-B reliability adapter No-Go；`final+aux logits` residual 后续被 Round 3 打穿 | 已完成，历史动机 |
| Round 3 Branch-Boundary Residual | 检验 aux logits / branch gaps 是否包含 final head 未显式消费的 branch-level predictive cues | best primary 低于 original，并被 weighted-average ordinary combiner control 打穿 | No-Go for current D3 offline residual；R3-D training-time residual 是 Not-Unlocked |
| Round 4 First-Principle Boundary Rebuild | 从 class-conditional geometry、low-rank error subspace、memory diagnostic、domain shortcut audit 重新验证 final-boundary 可干预结构 | R4-A/R4-D/R4-C 低于 original，R4-B 仅 Diagnostic-only | No-Go for current D3 offline patches / 归档 |
| Round 5 Training-Dynamics Rebuild | Gate-0 后只剩 image-branch/final gradient conflict 候选信号；R5-A 已按强对照 smoke | R5-A primary 低于 deterministic，且被 `aux_weight_2p0` control 打穿；image conflict telemetry 改善未转化为主指标收益 | No-Go for current R5-A training implementation；R5 reserve/组合未被永久排除 |

## 论文主张

现有 PANDA 通过领域原型距离选择邻域，缓解多领域假新闻检测中的负迁移。但领域相似并不等价于迁移可靠。当前 selector v2、seed-recheck、R3/历史 R4/P0-B/P1-A/P1-B/P1-C、Round 2、Round 3 和 Round 4 结果显示，旧 selector/source-view/domain-gate/reliability/source-utility/aux-logit residual/离线 boundary correction 路线都尚不能支撑正式主方法。下一步更可信的方法论文口径，是把这些失败边界转化为训练期内生机制候选：branch-final gradient consistency、low-margin boundary stress、modality counterfactual consistency 和 class-preserving domain-nuisance suppression。

## 当前核心

方法规划状态：Round 5 Training-Dynamics Gate-0 与 R5-A 单项 smoke 已完成，当前无 `Primary-Candidate`。

2026-05-26 远端源码第一性原理审计后，Round 5 主线进一步收紧为：

```text
Branch-Evidential Boundary Rebuilding for PANDA
```

理由：PANDA 代码显示 source/domain/reliability/aux 信号进入 final boundary 的位置和梯度路径不对。PAD/GNS 是 hard top-k 且 self dominated，DCA 是样本无关 late prompt bias，prototype encoder/reconstruction 有断梯度风险，aux branch 只作辅助 BCE。第一阶段 Gate-0 已实际完成，结果未满足 `G0-A/G0-D/G0-E` 同向条件：G0-E 只关闭当前 frozen arbitration probe，G0-D 不能支持当前 boundary-stress 训练许可，G0-S 只关闭当前 source/prompt frozen probe。因此不能进入 R5-Prime / R5-A+D seed42 smoke；随后 R5-A 单项 image-branch/final gradient consistency smoke 已完成并 `No-Go for current training implementation`，不复核 seeds、不扩 Weibo。R5-Prime/R5-A+D/R5-S 与 R5 reserve 仍需新 manifest 才能被进一步判断。

1. R3-A：AuxLogitResidual，只验证受约束 residual 是否优于普通 final+aux combiner。
2. R3-B：BranchDisagreementResidual，验证 branch-final gap/std 是否定位 boundary mismatch。
3. R3-C：BranchDrop Attribution，确认收益来自具体 branch、branch pair 还是 disagreement 结构。
4. R3-D：Training-time Endogenous Branch Residual，只有 offline controls 过线后才迁回训练期内生模块。

支撑证据与 fallback：

1. 以 `confidence_uncertainty = 1 - max(y_score, 1-y_score)`、fusion uncertainty、branch disagreement 等信号做 reliability/uncertainty evidence。
2. 记录 clean branch/fusion selector、uncertainty-aware stable-source selector、R3/R4/P0-B/P1-A/P1-B/P1-C 和 Round 2 P2-A/P2-C/P2-D 的 scope-limited No-Go / Blocked 边界，避免把失败路线包装成方法，也避免把未充分验证的方向错杀。
3. 保留 deterministic top-k、calibration-only、random、shuffled、parameter-matched controls 作为强对照。
4. 用 ECE、Brier score、high-confidence error、weak-domain F1 和 repeated eval variance 做可靠性与稳定性分析。

实现约束：

- Confidence uncertainty 必须使用 detach 版本，降低模型自反馈嫌疑。
- 必须消融 deterministic、confidence-uncertainty、overconfidence-only、random，以及 branch/fusion clean variants 的失败对照。
- Deterministic selector 必须作为独立强对照，不能和 uncertainty-aware selector 混在一起解释。
- Uncertainty/stability score 不能用 `is_error` 监督训练；组合权重、prototype 和超参只能使用 train/val。
- Gate 必须报告 bootstrap 95% CI、permutation test；high-confidence enrichment 必须报告 count、平滑 odds ratio、Fisher exact test 或 bootstrap CI。
- Neighbor selection fields 已导出，用来证明 uncertainty/stability signal 不只是与错误相关，也确实影响邻域迁移行为；但现有 selector seed-recheck 未通过，因此只能写作诊断和失败边界。
- 在 test confirmatory analysis 前，应先保存 gate 配置与 val-selected 权重，避免“看 test 错误设计方法”的嫌疑。
- 组合分数主结果优先用 z-score 后等权组合；val 调权只作为附录或消融。
- Selector behavior gate 至少报告 high/low-uncertainty neighbor Jaccard change、selection entropy 或 frequency、PAD/neighbor margin、弱域 selection frequency。
- 统计不确定性优先用 domain-stratified bootstrap 或 seed-aware bootstrap。
- High-confidence error 富集必须与 overconfidence-only 对照，证明不是单纯主分类器过度自信。
- R4 三 seed val 过线前不导出、不打开、不分析 test；不能根据 test 改 `lambda_view`、`lambda_cons`、view source、primary config 或 reliability 权重。

## 当前实验包

已完成：

- Weibo-21，3 seeds。
- Weibo，3 seeds。
- MMDFND reproduced，3 seeds。
- DAMMFND reproduced，3 seeds。
- PANDA reproduced，已有。
- selector v2 Go/No-Go 与 winning-control seed-recheck。结论：clean branch/fusion selector 与 uncertainty-aware stable-source selector 均未通过稳定性要求。

后续不再作为“新方法主表”继续扩展；当前论文/报告实验包应改为：

- reproduced baseline 主表 mean ± std。
- reliability / uncertainty diagnostic 表。
- failed selector hypotheses 表。
- per-domain F1/Acc/AUC。
- domain-to-neighbor heatmap。
- reliability / uncertainty score 分布。
- high-confidence error analysis。
- repeated-forward variance / selector stability analysis。
- ECE / Brier score。

若未来重新设计新方法，最低结果形态仍是：

- 新方法至少在一个数据集上稳定提升 0.5 个百分点以上，另一个数据集不退化。
- High-confidence error rate、repeated eval variance、弱域 F1 至少两个明显改善。
- 如果只提升 0.1-0.2 个点，必须有很强的机制证据，否则 PRCV/同档会议仍危险。

## 写作一句话

若只能写 fallback 证据，不要写成“PANDA 的稳定化后处理”，要写成：

```text
Reliable neighbor-domain adaptation for multimodal fake news detection should be uncertainty-aware: uncertain target samples should select source domains that are not only similar in domain prototypes but also stable under the model's reliability estimates.
```

若未来新的 Round 5/Round 6 候选重新 Gate-0、seed42 smoke 与三 seed val 后续通过，再改为对应方法主张，例如：

```text
PANDA's residual errors may arise from training-time gradient or modality reliance dynamics that prevent useful branch and reliability signals from being internalized by the final decision boundary.
```

## 下一步

1. 暂停 clean Reliability-aware Disagreement selector、uncertainty-aware stable-source selection 和 R3 Regret Router 的两数据集三 seed 大跑。
2. 记录 R3/R4/P0-B/P1-A/P1-B/P1-C、Round 2、Round 3 和 Round 4 的 scope-limited gate 结论，作为 Round 5 设计约束；P1-B 是 `Blocked/current checkpoint unsupported`，D2/D3 结论不得外推为方法族失败。
3. Gate-0 与 R5-A 单项 smoke 已完成并止损：不启动 `Branch-Evidential Boundary Rebuilding` / `Boundary-Stressed Branch-Consistent PANDA` 组合 smoke，不复核 R5-A seeds，不扩 Weibo；若继续方法线，必须另立新候选。
4. 任一候选核心功能逻辑失败或被 stacking/calibration/random/shuffled/parameter controls 打穿，按 `level_reached` 落状态并切换下一个：`D0/D1` 不写 No-Go，`D2/D3` 只关闭当前 probe/offline/frozen 变体，`D4` 才关闭当前训练实现；任一候选先可行也只标记 `Feasible-A/B`，继续验证剩余候选。
5. 已补 prediction-level repeated-forward `y_score` variance export，避免只用 selector entropy/frequency 讲稳定性；该结果只作为强对照和证据，不能证明 stable-source 方法通过。
6. 主表只使用 PANDA / MMDFND / DAMMFND reproduced baseline；当前没有 Round 5 候选进入三 seed val，不开启正式新方法主表。
