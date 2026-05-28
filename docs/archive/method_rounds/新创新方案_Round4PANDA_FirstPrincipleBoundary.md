# Round 4 PANDA 方法候选：First-Principle Boundary Rebuild

日期：2026-05-26

状态说明（2026-05-28 更新）：Round 4 first-principle boundary rebuild 已归档为 `No-Go for current D3 offline patches / Diagnostic-only`。Round 6/7 当前作用域验证已闭环且无 `Primary-Candidate`；新的待执行规划入口为 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 和 `round7_candidate_registry.md`。验证深度复审后，R4-A/R4-D/R4-C 只否定当前离线 class-geometry / low-rank / memory patch，不永久排除训练期 class-conditional margin regularizer、low-rank boundary adapter 或 memory regularization；若重开必须新 manifest + D4。

## 定位

这里的 Round 4 是 Round 3 branch-boundary residual 之后的新一轮候选池，不是历史文档 `新创新方案_R4PANDA_CounterfactualConsistency.md` 中的 R4-PANDA non-self source-view 路线。

当前结论已经很清楚：

- R3-PANDA Regret Router：`No-Go for current D4 R3 v0`，soft route 完全 self-domain collapse；全新 self-suppressed mixture 需新 D2/D3 -> D4。
- 历史 R4 non-self source-view consistency：`No-Go for current D2 PAD-top2 forced-view probe`，PAD top2 被 shuffled / bottom / random controls 打穿。
- P0-B DCA/source-view：`No-Go for current D2 late DCA/source-view probe`；sample-conditioned prompt/source training 未被排除。
- P1-A feature-aware PAD：`No-Go for current D2 hard feature-aware ranking probe`；soft/EMA prototype 未被排除。
- P1-B domain gate：`Blocked/current checkpoint unsupported`，不是 domain-conditioned expert 方法族失败。
- P1-C reliability/evidential：`No-Go for current D4+D5 reliability/selector implementation`，保留 reliability/calibration 诊断。
- Round 2 P2-A/P2-B/P2-C/P2-D：均未产生 `Primary-Candidate`，且 D3 结论只覆盖当前 offline/frozen 变体。
- Round 3 branch-boundary residual：`No-Go for current D3 offline residual gate`，best primary `0.949593/0.949593/0.987171` 低于 original `0.956086/0.956098/0.987382`，且被 `weighted_average_final_aux_logits` control `0.956093/0.956098/0.987499` 打穿。
- Round 4 first-principle boundary rebuild：`No-Go for current D3 offline patches / Diagnostic-only`，R4-A/R4-D/R4-C 离线 gate 均低于 original final score，R4-B 仅作为 domain shortcut 诊断。

因此 Round 4 不再沿以下方向续参：

```text
PAD/source-domain reranking
source-view intervention consistency
reliability/uncertainty selector
domain-gate implementation repair
aux-logit / branch-boundary residual
```

Round 4 的目标仍然是方法性论文，而不是把诊断报告升为主线。诊断材料只作为动机、强对照和失败边界证据。新的候选必须从第一性原理重新回答：

```text
PANDA 的最终错误究竟来自哪一种可干预的边界结构，
这种结构能否在 train/val-only、强对照、无 test 选择的协议下被稳定改变？
```

## 从失败规律推出的新约束

已有实验给出的硬约束：

1. 改 neighbor set 不等于改 final classifier boundary。
2. source-domain prompt / DCA 的扰动存在，但太弱，且 PAD ranking 不能打过 shuffled controls。
3. reliability / uncertainty 能解释错误和高置信错误，但转成 selector 或 correction 后 seed-sensitive。
4. aux logits 的 seed42 弱信号被 ordinary combiner 解释，不能写成 branch-boundary mechanism。
5. seed2024 多次暴露单 seed 偶然性，因此 seed42 只能做最小 gate，不能封主线。

Round 4 候选必须满足：

- 先做 frozen / offline feasibility gate，再考虑训练期模块。
- 每个候选只用 train 拟合、val 决策；三 seed val 过线前不导出、不打开、不分析 test。
- 若当前候选未过 gate，按 `level_reached` 标记 scope-limited status：`D0/D1=Evidence-only/Blocked/Provisional`，`D2/D3=当前 frozen/offline/probe 变体 No-Go`，`D4=当前训练实现 No-Go`。
- 若某候选可行，只标 `Feasible-A/B`，继续赛完其他候选。
- 所有候选最小 gate 完成后，再对可行候选深入复核并确定 `Primary-Candidate`。

## Round 4 候选池

### R4-A：Class-Conditional Boundary Geometry

优先级：最高。

第一性原理：

PANDA 的 domain prototypes / PAD 是 domain-centric，但假新闻检测最终边界是 label-centric。同一 source domain 内同时存在 fake / real，两类样本的迁移价值不同。若只按 domain 相似度选邻域，本质上可能把 label boundary 混掉。新的候选不再问“哪个 domain 更像”，而问：

```text
当前样本在 class-conditional cross-domain geometry 中，
是否靠近正确类别边界、错误类别原型或跨域类间冲突区？
```

最小 gate：

- 从 frozen PANDA 导出 train/val 的 final representation、`h_di`、`h_collab`、final logits、domain label 和 y label。
- 只用 train 构造 class-conditional prototypes：global class prototypes、domain-class prototypes、cross-domain class margins。
- 在 val 上只计算 metrics，不用 val label 调 prototype、阈值或超参。
- 检查 class-conditional margin 是否比 domain-only PAD margin 更能解释错误、low-margin flip 和弱域失败。
- 训练一个极小 class-conditional boundary residual 或 prototype-distance correction，只作为 offline feasibility，不直接写方法成功。

强对照：

- final-only Platt / temperature / isotonic。
- final-only linear / MLP。
- domain-only prototypes。
- class-prior-only correction。
- shuffled train labels。
- random class prototypes。
- same-parameter random feature residual。
- duplicate-final logits。

Go：

- val F1/Acc 不低于 original final score，并且收益不能被 final-only / random-label / domain-only controls 解释。
- class-conditional margins 在 low-margin 或 weak-domain bins 上有净收益。
- wrong->correct 明显多于 correct->wrong。

No-Go：

- 只改善 AUC/ECE/Brier，不改善或损害 F1/Acc。
- shuffled labels / random prototypes 同样有效。
- 收益只来自 final-only calibration。

若通过：

- 标记 `Feasible-A`。
- 训练期版本优先设计为 class-conditional prototype alignment / boundary-margin regularizer，而不是 post-hoc adapter。

### R4-B：Domain Shortcut / Invariance Boundary Audit

优先级：高。

第一性原理：

若 final representation 中含有过强 domain shortcut，模型可能用 domain distribution 近似 label boundary。PANDA 的 domain-aware 设计本来想借域信息帮助迁移，但当前多条 source-domain 方法失败，说明问题可能不是“域信息没用够”，而是“域信息进入边界的方式不对”。

核心问题：

```text
final representation 中是否存在可线性解码的 domain shortcut，
且该 shortcut 与错误、弱域和边界 margin 相关？
```

最小 gate：

- train-only 训练 domain probe：从 `h_di`、`h_collab`、final representation 预测 domain。
- train-only 训练 label probe，比较 domain-predictive directions 与 label-predictive directions 的夹角 / overlap。
- 在 val 上检查 domain-probe confidence 是否富集错误、低 margin、弱域。
- 做 frozen subspace intervention：移除或压低 top domain-predictive directions，再观察 final score / probe score / val F1。

强对照：

- shuffled domain labels。
- random subspace removal。
- class-predictive subspace removal。
- same-rank PCA removal。
- domain one-hot calibration control。
- adversarial / IRM / REx 只作为二阶段参考，不进入 primary。

Go：

- domain probe 准确率显著高于 shuffled control。
- domain shortcut 与错误或弱域退化相关。
- 移除受控 domain subspace 能改善或至少不损害 F1/Acc，同时降低错误富集。

No-Go：

- domain 可预测但与错误无关。
- 去 domain subspace 损害 F1/Acc。
- random subspace removal 同样有效。

若通过：

- 标记 `Feasible-A/B`。
- 训练期版本可设计为 class-preserving domain-orthogonalization 或 adversarial shortcut removal，但必须保留 label boundary。

### R4-C：Supervised Sample-Memory Boundary Patch

优先级：中高。

第一性原理：

PANDA 的 domain prototype 是粗粒度 domain memory；但错误常发生在样本级边界附近。若 domain prototype 太粗，真正有价值的不是“相似 domain”，而是 train split 中 label-aware 的局部邻域。

核心问题：

```text
在 final representation 上，train-only label-aware memory 是否能稳定修正 near-boundary val 样本，
并且不是简单 kNN 后处理或数据泄漏？
```

最小 gate：

- 只用 train representation 建立 sample memory。
- 对 val 样本取 kNN / prototype-neighbor vote / metric residual。
- residual 只在 final low-margin 样本上受限开启。
- 不使用 val/test label 建 memory、调 k、调阈值或挑 weak domain。

强对照：

- random memory。
- shuffled train labels。
- class-prior vote。
- same-k unlabeled memory。
- final-only calibration。
- logistic stacking / final-only MLP。
- duplicate train memory。

Go：

- val F1/Acc 有净提升，且 random/shuffled/class-prior controls 不能解释。
- 主要收益定位在 low-margin 样本，high-confidence correct 样本不被大量翻错。
- memory contribution 可压缩为训练期可复现模块。

No-Go：

- 只像 kNN post-hoc classifier。
- 对 k / threshold 极端敏感。
- shuffled label memory 同样有效。

若通过：

- 标记 `Feasible-B` 起步，因为审稿风险高。
- 只有转成训练期 supervised memory regularization / contrastive class memory 后，才允许竞争 `Primary-Candidate`。

### R4-D：Error Subspace / Low-rank Boundary Correction

优先级：中。

第一性原理：

若 PANDA 的错误集中在某些表示方向上，可能存在一个低维 error subspace。与其继续改 source selector，不如直接验证 final representation 是否存在可学习、可约束、可复现的低秩边界修正方向。

核心问题：

```text
train split 中由 low-margin / train-error / disagreement 样本诱导的低秩方向，
是否能在 val 上修正同类边界错误，而不是训练一个错误检测器？
```

最小 gate：

- 只用 train 构造低秩方向：train low-margin、train misclassified、class-conditional residual、domain-balanced residual。
- 在 val 上应用小幅 logit / feature correction。
- gate 必须报告 correction norm、activation rate、margin-bin gain 和 flip audit。

强对照：

- random low-rank directions。
- shuffled train labels。
- train-correct subspace。
- final-only linear / MLP。
- Platt / temperature / isotonic。
- same-rank PCA subspace。

Go：

- val F1/Acc 不低于 original，且 low-margin bin 有净收益。
- wrong->correct 多于 correct->wrong。
- random / PCA / shuffled controls 不可解释。

No-Go：

- 变成 train-error detector，跨 seed 不稳定。
- high-confidence correct 样本翻错过多。
- final-only MLP 同样达到。

若通过：

- 标记 `Feasible-B`。
- 训练期版本必须是低秩 adapter / boundary regularizer，而不是离线后处理。

## Round 4 执行顺序

真正执行前必须按以下顺序；该顺序与蓝军反审后的优先级一致，后续不得在看完 val 结果后回头改顺序：

1. Protocol draft：固定 splits、features、candidate list、controls、metrics、No-Go 线和输出 manifest。
2. Blue-team audit：源码链路、方法创新、实验门控、审稿风险四类反审。
3. Common frozen export：只导出 train/val representation/logits/domain/label，manifest 记录 SHA、row count、`test_split_exported=false`、`test_used_for_decision=false`。
4. R4-A class-conditional boundary geometry gate。
5. R4-D low-rank error subspace gate。
6. R4-C supervised sample-memory boundary gate。
7. R4-B domain shortcut / invariance gate。
8. 汇总所有候选：`No-Go` / `Feasible-A` / `Feasible-B`。
9. 只对所有候选赛完后的可行方案做 seed42 training smoke。
10. seed42 训练过线后，复核 seeds 2024/2026。
11. 三 seed val 过线后，才考虑 Weibo 扩展。
12. 所有 val 决策完成后，test 只做一次 confirmatory。

## 写作边界

可以写：

```text
The previous source-routing and auxiliary-logit hypotheses failed under strong controls. We therefore rebuild the intervention space around class-conditional decision geometry and domain-shortcut invariance, and only promote a candidate after train/val-only feasibility gates and control moats.
```

不能写：

```text
We propose a diagnostic paper because all methods failed.
```

也不能写：

```text
We improve PANDA by adding another post-hoc classifier.
```

Round 4 的论文目标必须是可内生到模型训练的边界机制。如果一个候选只在离线后处理里可行，最多记为 `Feasible-B`，不能直接升为 `Primary-Candidate`。

## 当前决策

当前没有 `Primary-Candidate`。Round 4 已完成 seed42 train/val-only protocol、common frozen export 与四候选最小 gate。经蓝军反审后，执行顺序为：

```text
R4-A Class-Conditional Boundary Geometry
 > R4-D Error Subspace / Low-rank Boundary Correction
 > R4-C Supervised Sample-Memory Boundary Patch
 > R4-B Domain Shortcut / Invariance Boundary Audit
```

理由：R4-A 和 R4-D 最直接指向 final decision boundary 的几何与误差结构，方法张力最高；R4-C 容易被审稿人看成 kNN 后处理，只能先作为 boundary upper-bound / diagnostic；R4-B 更适合作为 domain shortcut falsification 和审稿防御，除非 gate 证明 domain shortcut 与错误存在可干预对齐，否则不抢主线。

实际 gate 结果：

- Common frozen export：`remote_panda_work/repro_logs/round4_first_principle/common_frozen/`，只含 Weibo-21 seed42 train/val，`test_split_exported=false`、`test_used_for_decision=false`。
- R4-A Class-Conditional Boundary Geometry：`No-Go for current D3 offline class-conditional residual patch`。Best primary `r4a_class_conditional_final_residual` val F1/Acc/AUC `0.926817/0.926829/0.977039`，低于 original `0.956086/0.956098/0.987372`；wrong->correct 7、correct->wrong 25。
- R4-D Error Subspace / Low-rank Boundary Correction：`No-Go for current D3 offline low-rank correction patch`。Best primary `r4d_lowrank_error_subspace_rank4` val F1/Acc/AUC `0.944714/0.944715/0.985383`，低于 original；wrong->correct 5、correct->wrong 12；label-shuffled / random / PCA controls 均能接近或打穿。
- R4-C Supervised Sample-Memory Boundary Patch：`No-Go for current D3 offline sample-memory residual patch`。Best primary `r4c_low_margin_memory_residual` val F1/Acc/AUC `0.938192/0.938211/0.977218`，低于 original；class-prior memory residual 与 final-confidence threshold controls 不改标签并与 original 持平，说明离线 memory 不能升主线。
- R4-B Domain Shortcut / Invariance Audit：Diagnostic-only。Domain probe val accuracy `1.000000`，shuffled-domain control `0.253659`，但 domain confidence 对错误 AUC 仅 `0.578042`；domain-subspace removal 反而损害 label probe 到 F1/Acc `0.938210/0.938211`。

结论：Round 4 本轮无 `Feasible-A/B`，不启动本轮 seed42 training smoke，不复核 seeds 2024/2026，不扩 Weibo，不导出/打开/分析 test。后续若继续方法论文，不能在这些离线 boundary correction 旧实现上继续调参；必须提出本质不同的训练期内生机制并新建 manifest，或转向 diagnostic/fallback 写作。
