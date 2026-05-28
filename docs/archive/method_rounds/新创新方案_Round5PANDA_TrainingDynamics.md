# Round 5 PANDA 方法候选：Training-Dynamics Rebuild

日期：2026-05-26

状态说明（2026-05-28 更新）：Round 5 active Gate-0 与 R5-A 单项 seed42 smoke 已完成；R5-A `r5a_image_project_l1p0` 当前训练实现判定 No-Go，G0-E/G0-S 只否定当前 frozen/probe 变体，R5-Prime/R5-A+D/R5-S 与 reserve 候选是 `Not-Unlocked / Not-Evaluated`，不是方法族永久失败。本文档保留为历史训练动力学候选记录。Round 6/7 当前作用域验证已闭环；新的待执行规划入口为 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 和 `round7_candidate_registry.md`；不得继续沿 R5-A image projection 旧实现续参。

## 定位

Round 5 是 Round 4 first-principle boundary rebuild 的当前 D3 offline patches 均 `No-Go / Diagnostic-only` 之后的新一轮方法候选池。它不再继续旧 PAD/source-domain reranking、reliability selector、aux-logit residual、forced source-view intervention 或离线 boundary correction；训练期 class/memory/low-rank regularizer 若重开需新 manifest + D4。

当前事实源：

- PANDA reproduced baseline、MMDFND、DAMMFND 两数据集三 seed 已完成。
- R2、R3 Regret Router、历史 R4 non-self source intervention、Round 2、Round 3 branch-boundary residual、Round 4 first-principle boundary rebuild 均未产生 `Primary-Candidate`。
- Round 4 已证明 class-conditional prototype residual、low-rank error subspace、sample-memory residual 都会在 val 上翻错更多原本正确样本；R4-B 只能作为 domain shortcut diagnostic。

Round 5 的核心判断：

```text
旧路线不是缺一个更强的 selector 或离线头，
而是有效诊断信号没有在训练期稳定内生进 final classifier boundary。
```

因此新的候选必须直接作用于训练动力学：loss、gradient、representation stress、modality intervention、domain nuisance suppression，而不是在 frozen prediction 或 final logit 后面再接补丁。

## 外部方法谱系与可借鉴点

PANDA 原论文的命题是从 blind transfer 转向 prototype-driven wise selection：DMPG 学 domain modal prompts，PAD 度量方向性 transferability，GNS 选择邻域，DCA 融合源域知识。我们的复现和 gate 说明这条 source-selection 链路在当前实现和数据上很难继续提升 final boundary，因此 Round 5 只借 PANDA 的 `h_di + h_collab` 结构，不再沿 source ranking 续参。

可借鉴但不能照搬的外部路线：

- Multi-task gradient surgery / CAGrad：PANDA 同时优化 final BCE、text/image/fusion aux BCE 和 reconstruction loss，天然可能存在 gradient conflict。可借鉴 PCGrad / CAGrad 的“冲突梯度处理”，但必须落在 PANDA branch-final 训练动力学上，不能变成通用多任务 baseline。
- Modality disruption / modality dropout：多模态假新闻检测中某些模态可能是 disruptive 或 over-expressive。可借鉴 modality counterfactual / dropout consistency，但不能重新包装 CLIP conflict 因果线。
- Domain generalization REx / Fishr / GroupDRO：可借鉴 group risk / gradient variance / worst-domain 思想，但 DomainBed 经验提醒普通 DG 算法经常打不过强 ERM，因此必须把它作为强对照或条件机制，不允许直接套壳。
- Robust perturbation training / VAT / TRADES / R-Drop / SAM：可借鉴边界压力训练，但必须证明 stress 作用在 PANDA 的 `h_di/h_collab/h_final` 边界，而不是额外 epoch、普通 dropout 或通用鲁棒正则带来的收益。

2026-05-26 外部谱系与蓝军反审补充：

- PANDA 原始问题是多源负迁移与 asymmetric domain relation；我们的新方案必须解释为什么 source/domain/reliability 信号没进入 final boundary，而不是继续换一个 source selector。
- 多任务梯度文献提醒：直接上 PCGrad/CAGrad 不等于解决冲突，必须报告 layer-wise / representation-level conflict 是否真实存在，以及 conflict 下降是否与 low-margin、weak-domain、HCE 改善同向。
- 多模态 imbalance / modality dominance 文献提醒：modality-drop consistency 有价值，但多模态假新闻中“图文不一致”本身可能是 fake cue；因此 R5-B 只允许保守的同样本内退化视图，不做跨样本图文替换。
- Domain generalization 文献提醒：普通 DANN/IRM/REx/Fishr/GroupDRO 极易被强 ERM 打穿；R5-C 必须先证明 label-conditional domain nuisance 与错误相关。
- Boundary-stress 路线有潜力，但若只是 `PANDA + VAT/SAM/FGM` 就是套壳；必须限定在 PANDA 的 `h_di/h_collab/h_final` 低 margin 区域，并证明 high-confidence correct 不被翻坏。

## 已禁止续参方向

Round 5 禁止把以下方向换名重开：

```text
PAD/source-domain reranking
non-self source-view consistency
reliability/uncertainty selector or correction
aux-logit residual / branch-boundary late fusion
domain-gate implementation repair
offline class-prototype / low-rank / memory boundary correction
test-derived weak-domain or threshold tuning
```

若一个候选只能在 frozen/offline prediction 上工作，最多作为 diagnostic，不得进入 `Primary-Candidate`。

## 候选池

### R5-A：Gradient-Consistent Branch Training

优先级：P0 诊断最高；可作为主线机制的一半，但不建议单独包装成“PANDA + PCGrad”。

第一性原理：

PANDA 已有 text/image/fusion auxiliary heads，说明分支被监督过；Round 3 证明 aux logits 有弱信号但作为 late fusion 会被 ordinary combiner 打穿。新的问题不是“把 aux logits 拼进去”，而是：

```text
aux losses 是否在训练中与 final loss 发生梯度冲突，
导致分支学到的有用信号没有进入 final boundary？
```

核心机制：

- 在 `text_features`、`image_features`、`fusion_features` 或共享专家参数上记录 final BCE 与三个 aux BCE 的 gradient cosine。
- 若存在负 cosine 或极端梯度幅值不均衡，则优先考虑 PANDA-specific branch-final alignment、冲突层 partial detach、adapter split 或 sparse update；generic PCGrad/CAGrad 只作为强对照。
- 只处理训练期梯度，不新增 inference-time feature、logit 或 memory。

最小 Gate-0：

- Weibo-21 seed42，deterministic selector，5 epoch。
- 先跑 diagnostic-only 版本：不改变训练，只记录 branch-final gradient cosine、gradient conflict rate、per-branch gradient norm、val F1/Acc/AUC/ECE/HCE。
- 输出 conflict-rate by domain、low-margin bin、wrong/correct、HCE bin，并记录冲突层位置。
- 若 conflict rate < 10%-15%，或 conflict 与 error/low-margin/weak-domain 无关，不进入训练版。

Primary smoke：

```text
L = L_final + mean(L_text, L_image, L_fusion) + lambda_rec L_rec
  + lambda_gc * conflict_penalty_or_projected_gradient
```

强对照：

- original PANDA Gumbel、deterministic eval、deterministic train。
- aux loss weight sweep。
- PCGrad generic baseline。
- CAGrad / GradNorm / MGDA 或 OGM-GE 中至少选择一个可实现强对照。
- random-sign gradient penalty。
- branch dropout only。
- same-forward-budget / same-epoch control。
- Round 3 weighted-average final+aux 只作为失败风险对照，不作为训练目标。

Go：

- val Macro-F1/Acc 不低于 deterministic，最好至少 +0.3pp。
- gradient conflict rate 下降，且下降与 low-margin / weak-domain / HCE 改善同向。
- wrong->correct 多于 correct->wrong。

No-Go：

- diagnostic 显示 branch-final gradient conflict 不存在或很弱。
- F1/Acc 低于 deterministic。
- 只改善 ECE/Brier/HCE，不改善主指标。
- generic PCGrad / aux weight sweep 同样达到或更好。

### R5-B：Training-Time Modality Counterfactual Consistency

优先级：P0/P1 诊断；可作为二阶段增强，不作为第一主线。

第一性原理：

CLIP-only conflict 已不能主打，但 PANDA 的错误和高置信错误与 branch disagreement、fusion uncertainty、confidence uncertainty 相关。新问题是：

```text
final boundary 是否过度依赖某个过表达或不稳定模态，
导致遇到模态扰动时出现高置信错判？
```

核心机制：

- 训练时构造 full view、text-preserved view、image-preserved view、fusion-drop view；只做同样本内轻量退化或 masking，不做跨样本图文替换。
- 对 full view 做 CE；对 dropped views 做 label-preserving consistency / bounded CE。
- 对分支依赖做 entropy 或 balance 约束，避免 collapse 到单模态。
- 不使用 CLIP-only conflict 作为主因果解释。

最小 Gate-0：

- Weibo-21 seed42，deterministic selector，5 epoch。
- 先做 batch smoke：确认 modality-drop views 真实改变 `h_di/h_final/logits`，且不是简单置零后数值崩溃。
- 导出 modality-drop score delta、view flip rate、branch reliance entropy、HCE、weak-domain F1。

强对照：

- 普通 dropout。
- random modality mask with same rate。
- consistency-only without label CE。
- label smoothing / confidence penalty / R-Drop。
- branch_fusion_clip old control。
- same-parameter MLP / same-forward-budget control。
- label-shuffled mask schedule。

Go：

- val Macro-F1/Acc 不低于 deterministic。
- HCE 或 low-margin bin 至少一项明显改善，且 weak-domain 不退化。
- branch reliance 不 collapse 到单模态。

No-Go：

- 普通 dropout 或 random mask 同样有效。
- full-view 主指标下降。
- branch reliance collapse。
- 结果可由 CLIP-only conflict 解释。
- view 不是 label-preserving，或 modality inconsistency cue 被 consistency loss 抹掉。

### R5-C：Class-Preserving Domain-Nuisance Suppression

优先级：P1，必须先过 shortcut-error diagnostic；默认不作为第一主线。

第一性原理：

R4-B 显示 domain label 在 `h_final` 中非常容易线性解码，但 domain confidence 与错误关系较弱，直接去 domain subspace 会伤 label boundary。因此新问题不是“去掉 domain 信息”，而是：

```text
能否只压制 label-irrelevant 的 domain nuisance，
同时保留 class-discriminative boundary？
```

核心机制：

- 在 `h_di` 或 `h_final` 上加 conditional domain adversary：在 label 条件内混淆 domain。
- 或使用 class-conditional REx/Fishr：对同一 label 内不同 domains 的 risk/gradient variance 做约束。
- 必须配 class-preservation loss，避免把 label boundary 一起抹掉。

Gate-0：

- 先用 train/val-only 复核：domain-probe confidence 是否在同 label 条件下仍与 error / low-margin / weak-domain 相关。
- 必须同时报告 label probe / class margin 是否保持，避免把 class-discriminative domain cue 当 nuisance 压掉。
- 若 conditional domain-error AUC 不显著高于 random/shuffle，直接 Diagnostic-only，不开训练。

强对照：

- unconditional adversary。
- domain-label shuffle adversary。
- random partition adversary。
- GroupDRO / REx / Fishr alone。
- domain one-hot calibration。
- same-param ERM。

Go：

- val Macro-F1/Acc 不低于 deterministic。
- worst-domain F1 或 weak-domain F1 改善。
- domain nuisance probe 降低，但 label probe / class margin 不塌。

No-Go：

- domain probe 降了但 F1/Acc 掉 >0.3pp。
- random/shuffled domain controls 同样有效。
- conditional domain-error diagnostic 不成立。

### R5-D：PANDA Boundary-Stress Training

优先级：Gate-0 前为 P0/P1 机制组合候选；Gate-0 后已降级为 destructive boundary fragility 证据。单独写风险较高，且当前不能与 R5-A 组成主线。

第一性原理：

Round 4 离线边界补丁会翻错更多正确样本，说明 post-hoc correction 太粗。新的问题是：

```text
能否在训练期对 PANDA final representation 的低 margin 区域施加温和压力，
让边界变宽而不是事后翻标签？
```

核心机制：

- 在 `h_di/h_collab/h_final` 上做 small-norm adversarial or random perturbation。
- 约束 full logits 与 perturbed logits 的 consistency，同时保持 label CE。
- 只在 train low-margin 或 high-uncertainty 样本上启用，避免伤害 high-confidence correct 区域。

Gate-0：

- 先用已有 train/val frozen representation 做边界敏感性诊断：对 `h_di/h_collab/h_final` 加同范数微扰，记录 logit delta、flip rate、margin shrinkage、correct->wrong、wrong->correct。
- 必须按 low-margin/high-confidence-correct/domain 分桶；若低 margin 区域不比随机样本更敏感，或 correct->wrong 远多于 wrong->correct，R5-D 不开训练。
- 若 G0-A 证明 branch-final conflict 集中在低 margin / weak-domain，且 G0-D 显示同一区域边界脆弱，则优先组合成 A+D 主线。

强对照：

- VAT / TRADES / R-Drop / SAM。
- FGM/PGD adversarial training、manifold mixup、hard example mining、label smoothing / focal loss。
- random perturbation same norm。
- high-confidence perturbation。
- focal / margin-only loss。
- extra epoch / lr control。

Go：

- low-margin bin 净收益为正。
- high-confidence correct 翻错不上升。
- 主指标不低于 deterministic，最好 +0.3pp。

No-Go：

- 通用 VAT/TRADES/SAM 同样或更好。
- 只改善校准，不改善 F1/Acc。
- perturbation 主要破坏 correct samples。

### R5-E：Training-Time Class Memory Regularization

优先级：P3，仅作二阶段候选。

定位：

离线 supervised memory patch 已 No-Go，不能做 kNN 后处理。若保留，只允许作为训练期 class memory regularizer：用 batch / queue 中的 same-class cross-domain positives 与 different-class negatives 调整 representation。

强对照必须包含 SupCon、plain kNN、label-shuffled memory、random memory、class-prior memory、final-only calibration。

若 inference 需要查 train memory，`claim_scope=current primary deployable method`，可直接 No-Go for primary method；但训练期 memory regularizer / contrastive queue 若不依赖 inference train memory，需另立 manifest 并通过 D3 upper bound -> D4。

## Gate-0 前推荐主线假设

蓝军反审后的推荐不是单押某一个现成算法，而是先验证以下组合命题：

```text
PANDA 的 source/reliability/aux/domain 线索之所以不能稳定提升，
是因为 final boundary 附近同时存在 branch-final 梯度冲突和 representation boundary 脆弱性。
```

Gate-0 前假设：若 G0-A 与 G0-D 同时成立，优先主线为：

```text
Boundary-Stressed Branch-Consistent PANDA
```

含义：

- R5-D 暴露并加宽 PANDA `h_di/h_collab/h_final` 的低 margin 边界。
- R5-A 只在边界脆弱区域或冲突层缓和 branch-final 更新冲突。
- 推理期不新增 aux-logit late fusion、不查 memory、不用 source/reliability selector。

Gate-0 后实际口径：G0-A 只保留 image-branch/final gradient conflict candidate signal；G0-D 是 destructive boundary fragility，不可作为当前 robust-boundary 训练许可。随后 R5-A 单项训练版已补 generic PCGrad/CAGrad/aux weight sweep、random-sign penalty 和 same-forward-budget controls 并完成 smoke，结论为 `No-Go for current r5a_image_project_l1p0 training implementation`。

2026-05-26 二次冻结与 Gate-0 结果：源码审计后，第一阶段执行口径已由旧 `G0-A/G0-B/G0-C/G0-D` 收紧为 `G0-A/G0-D/G0-E/G0-S`；`G0-B/G0-C/R5-P/R5-I` 降为 reserve。Weibo-21 seed42 train/val-only Gate-0 已完成：G0-A `Feasible-A`（image branch conflict rate `0.337662`，low-margin enriched=true）；G0-D `Feasible-B`（low-margin sensitivity 成立，但 boundary-shrink val F1/Acc `0.939832/0.939837` 低于 original `0.956086/0.956098`，correct->wrong 17 > wrong->correct 7）；G0-E `No-Go for current frozen branch-evidential arbitration probe`（branch evidential arbitration val F1/Acc `0.933129/0.933333`，低于 original 且 flip audit 5/19 负向）；G0-S `No-Go for current static/forced source-prompt probe`（PAD top2 CE `0.157783` 被 shuffled PAD top2 CE `0.156849` 打穿）。因此当前不解锁 R5-Prime / R5-A+D / R5-S；这些是 `Not-Unlocked`，不是组合或 prompt-fusion 训练期机制已失败。R5-A 单项训练版随后已完成并对当前 image projection No-Go。

2026-05-26 深度复盘口径降调：`G0-A` 的正信号主要来自 image branch，不能泛化到 text/fusion，也不能直接写成 low-margin/weak-domain 机制。Image conflict batch 的 low-margin rate 只比 non-conflict 高 `1.64pp`，error rate 只高 `1.17pp`；且梯度记录在 `model.train()`，margin/error context 来自 eval-mode frozen export，存在 train/eval 口径差异。`G0-D` 应视为 destructive boundary fragility：`h_di/h_final` 小扰动能集中翻动 low-margin 区域，但 17 个 correct->wrong 多于 7 个 wrong->correct；`h_collab` 几乎不动，说明 source/DCA late bias 弱。`G0-E` primary 与 shuffled branch-logit control 几乎同坏，`G0-S` 方向不稳且被 shuffled prompt/source 打穿。因此后续论文叙事只能说“image-branch/final gradient conflict 是候选训练期信号”，不能说 branch-evidential arbitration、source/prompt interaction 或 boundary-stress 已成立。

2026-05-26 R5-A 单项 seed42 smoke 已按预注册完成，结论为 `No-Go`。该 smoke 固定 train/val-only，显式 `--skip_final_test`，未导出、未打开、未分析 test；`G0-B/G0-C` 作为 superseded reserve 未进入当前决策。Variants 覆盖 deterministic_train、same-forward-budget/no-new-module、aux weight sweep、generic PCGrad/CAGrad、random-sign penalty 和 primary `r5a_image_project_l1p0`。结果显示 primary val F1/Acc `0.936504/0.936585`，低于 deterministic `0.938175/0.938211`，且被 `aux_weight_2p0` control `0.939837/0.939837` 打穿。Primary 虽降低 image conflict rate `0.106494 -> 0.058442`，但 flip audit 为 `9 wrong->correct / 10 correct->wrong`；因此不能写作 PANDA-specific image projection 成功。`aux_weight_2p0` 降低 image conflict rate 到 `0.024675` 且弱域 F1/HCE/ECE 更好，说明 aux supervision 强度是有价值的新观察，但它是 control 信号，若要继续必须单独立新候选并重新预注册。

## Round 5 执行顺序

1. 更新总控、TODO、session_start，登记 Round 5 为当前候选池。
2. Protocol freeze：固定 `allowed_splits=train/val`、primary candidate order、controls、metrics、No-Go 线、manifest。
3. 第一轮 Gate-0：并行或顺序跑 G0-A gradient conflict diagnostic、G0-D boundary sensitivity diagnostic、G0-E branch-to-final arbitration frozen probe、G0-S prompt/source interaction feasibility。
4. 第一轮主线判定：G0-A/G0-D/G0-E 同向成立时优先进入 R5-Prime / R5-A+D；只有 G0-A 成立时只允许考虑 R5-A 单项 smoke；G0-S 只有打过 shuffled/random/static late DCA controls 才能重开 source/prompt 路线。实际 Gate-0 后三者未同向，只保留降调后的 R5-A 单项候选；该候选已完成 smoke 并 `No-Go for current r5a_image_project_l1p0 training implementation`。
5. R5-A seed42 5-epoch smoke 已完成且对当前 image projection 训练实现 No-Go。
6. 当前没有 Round 5 可行候选进入 seeds 42/2024/2026 val 复核；R5-Prime/R5-A+D/R5-S 与 reserve 候选未直接 D4 验证时保持 `Not-Unlocked / Not-Evaluated`。
7. 后续如提出新候选，仍需重新执行 train/val-only Gate-0 与 seed42 smoke；三 seed val 过线后才扩 Weibo；所有 val 决策结束前不导出、不打开、不分析 test。

## 第一轮推荐

第一轮只做 Gate-0，不跑正式训练：

```text
G0-A: branch-final gradient conflict diagnostic
G0-D: low-margin boundary sensitivity diagnostic
G0-E: branch-to-final arbitration frozen probe
G0-S: sample-conditioned prompt / source interaction feasibility
```

推荐优先级：

1. G0-A + G0-D + G0-E：若三者同向成立，优先进入 R5-Prime / R5-A+D smoke。实际结果中 G0-E 当前 frozen probe No-Go、G0-D destructive，因此该分支为 `Not-Unlocked`。
2. R5-A 单项：已完成并对当前 image projection No-Go；primary 低于 deterministic 且被 aux-weight control 打穿。
3. R5-S：仅在 G0-S 打过 shuffled/random/static late DCA controls 后进入；当前 prompt-fusion training 是 `Not-Unlocked`。
4. R5-B/G0-B、R5-C/G0-C、R5-E、R5-P/R5-I：当前是 reserve / not evaluated，除非补直接机制 Gate-0 与协议，否则不抢第一阶段资源；不能折叠成 Round 5 No-Go。

最严 No-Go：

- 任何候选若只是把已失败的 PAD/source reranking、reliability selector、aux-logit residual、offline correction 当前变体换名续参，则在该 `claim_scope` 下 No-Go；本质不同训练期机制必须新登记 `claim_scope`、D-level 与强对照。
- 任一 seed val F1/Acc 低于 deterministic，不扩 seed、不扩 Weibo。
- 只有校准收益，没有 Macro-F1/Acc 收益，不写方法主表。
- Random/shuffle/same-param/generic baseline 持平或打穿，不写主贡献。
- 如果收益可由 PCGrad/CAGrad、普通 dropout、普通 DG、VAT/SAM/FGM、focal/label smoothing、SupCon/kNN 完整解释，不写成 PANDA 方法贡献。
