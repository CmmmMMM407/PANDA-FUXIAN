# Round 7：Risk-Aware Final-Boundary Learning

日期：2026-05-28

状态：`D4-LITE TRENDS RECORDED / FULL-D4 NOT-UNLOCKED / NO-PRIMARY-CANDIDATE`。本文件登记下一代候选方案与实验门控；2026-05-28 已完成 train/val-only artifact audit、R7-A/R7-B/R7-C/R7-D 当前 D2/D3 Gate-0、真实 batch `D3.5 Gradient-Sanity`，并对 R7-A/R7-D 补完 `D4-lite Training-Dynamics-Smoke`。当前未导出或分析 test，未解锁正式 5-epoch D4 smoke。

当前证据入口：

```text
tools/run_panda_round7_gate0.py
tools/run_panda_round7_d35_gradient_sanity.py
tools/run_panda_round7_d4_lite.py
remote_panda_work/repro_logs/round7_gate0/seed42/
remote_panda_work/repro_logs/round7_d35_gradient_sanity/seed42/
remote_panda_work/repro_logs/round7_d4_lite/seed42/
/root/autodl-tmp/panda_repro/panda/repro_logs/round7_gate0/seed42/
```

当前 Gate-0 摘要：

- Artifact audit `PASS`：train/val rows `4926/615`，`test_split_exported=false`、`test_used_for_decision=false`。
- R7-A D2 `Feasible-B` for current composite risk enrichment；D3 `No-Go for current risk-weighted offline proxy at D3`。
- R7-B D2/D3：`No-Go for current branch partition definitions at D2` / `No-Go for current teacher construction at D3`。
- R7-C D2/D3：`No-Go for current hard-region memory construction at D2` / `No-Go for current hard-region frozen memory proxy at D3`。
- R7-D D2/D3：`No-Go for current branch reliability rule at D2` / `No-Go for current aux-weight proxy at D3`。
- D3.5：R7-A risk-margin 可达但高度同向 CE，risk-consistency 与 CE 冲突，anti-overconfidence 梯度很小；R7-B agreement-KD 可达但 teacher 不干净，wrong-branch-suppression 不触达 final boundary；R7-C contrastive path 可达但 hard-region 与 all-sample/random controls 不分离；R7-D aux curriculum 只走 branch path。
- D4-lite：R7-A composite risk 短训 F1/Acc/AUC `0.732329/0.739837/0.866367`，优于 deterministic-lite 与 risk controls，标为 `D4-lite Feasible-B trend`；R7-D sample aux `0.630592/0.660163/0.836594` 低于 static aux 2.0 control `0.736521/0.739837/0.837197`，标为 `Not-worth-full-D4 for current lite setup`。
- 这些结论只关闭当前 risk definition、teacher construction、memory proxy 和 aux-weight proxy，或决定当前 lite setup 是否值得正式 D4；不关闭本质不同训练期方法族。D3.5/D4-lite 不能证明正式训练实现成功或失败。

## 主命题

下一代方法不再沿着“换 source、换 prompt、换 prototype、离线 adapter、推理期 selector”继续微调。新方法必须满足一个硬条件：

```text
把 reliability、branch conflict、low margin、weak domain 等风险信号
在训练期内生写进 final decision boundary，
而不是在推理期用 selector、router、adapter 或校准器事后补救。
```

暂定主线命名：

```text
Risk-Aware Final-Boundary Learning for Multimodal Multi-Domain Fake News Detection
```

中文表述：

```text
面向多模态多领域假新闻检测的风险感知 final 边界学习
```

## 本轮负结果抽象

1. **PANDA final boundary 很强**：大多数 offline/frozen patch 低于 original final，说明轻量后处理很难稳定加分。
2. **reliability / uncertainty 是好诊断，不是好 selector**：它能解释错误、高置信错误和弱域，但转成 source routing 或 inference selector 后 seed 不稳。
3. **source / prompt / prototype 信号多半是可扰动，不是可贡献**：PAD、DCA、prototype、prompt 都能改变 logits，但 random / shuffled / bottom controls 经常追平或打穿。
4. **branch / aux 信号有训练动态价值**：R5-A/R6-A 失败不等于 aux 无用，而是当前 image projection 和 aux schedule 没有比朴素 `aux_weight_2p0` 更像方法。
5. **低 margin 局部是边界弱点，但不能做离线主线**：R6-C seed42 弱正，seed2024/2026 不支持；低 margin 更适合作为训练采样或约束区域。

## 执行纪律

本轮所有候选都必须遵守 `创新方法验证深度复审.md` 的 D-level 规则：

| 深度 | 本轮含义 | 允许结论 |
| --- | --- | --- |
| `D0` | 规划、源码阅读、旧结果类比 | 只能写 hypothesis / risk prior |
| `D1` | 代码路径、输入字段或 artifact 不可达 | 只能写 `Blocked` |
| `D2` | 直接机制小实验，让核心信号作用到目标张量、样本权重、teacher partition 或 hard-region memory | 可关闭当前风险定义、partition 或 memory 构造；不能关闭训练期方法 |
| `D3` | train/val-only offline 或 frozen upper-bound gate | 可关闭当前 offline/frozen/proxy 变体；不能关闭训练期 loss / representation / final-boundary 方法 |
| `D3.5` | 真实 PANDA train batch forward/backward 梯度 sanity；候选 loss 必须产生 finite/nonzero 梯度，并报告与 CE 梯度的 cosine、norm ratio、risk/branch/hard-bin 梯度集中度 | 可判当前 loss 公式是否梯度不可达、退化为 CE/置信度换皮或与 CE 严重冲突；不能判性能 |
| `D4-lite` | Weibo-21 seed42 train/val-only 1-2 epoch mini-smoke，强 controls 同 budget，只看训练动态趋势 | 可判是否值得冻结正式 D4；不能判当前训练实现 No-Go 或 Primary |
| `D4` | Weibo-21 seed42 train/val-only 5-epoch smoke，含强 controls、flip audit、落盘 metrics | 可判当前训练实现 `No-Go` 或 `Feasible-A/B` |
| `D5` | Weibo-21 seeds 42/2024/2026 val 复核 | 可支持稳定性结论和 `Primary-Candidate` 排序 |

强制规则：

- `D0/D1` 不得写 `No-Go`。
- `D2/D3` 只能否定当前小实验、risk 定义、teacher partition、memory 构造或 offline 变体。
- 任何训练期 loss、representation、routing、aux curriculum 或 final-boundary 方法，至少到 `D4` 才能对当前训练实现写 `No-Go`；`D3.5` 和 `D4-lite` 只能作为“是否值得正式训练”的证据。
- 某个候选先过线时，只标记 `Feasible-A/B`，继续验证其余候选；四个候选全部完成对应 Gate 后，再对可行候选做深入验证。
- 三 seed val 过线前，不导出、不打开、不分析 test；不得用 test 选择 risk、threshold、lambda、teacher、memory 或弱域。

## 共用 artifact audit

开跑前必须先确认 train/val-only artifact 是否足够支持四条路线：

- final logits / score / margin / per-sample CE。
- text / image / fusion branch logits 或概率。
- `h_text / h_image / h_fusion / h_di / h_collab / h_final`，若缺失则先写 export gate。
- branch disagreement、branch agreement、confidence uncertainty、overconfidence、low-margin bin。
- domain/category label 与 train/val split 标识。
- 历史 loss volatility 若已有 per-epoch/per-sample loss；若没有，先把该项降级为 optional，不得因缺失直接 No-Go。
- modality inconsistency 可从 branch disagreement、view-drop delta 或 text/image/fusion branch error pattern 近似；近似定义必须有 shuffled/random controls。

## 候选优先级

| 优先级 | 编号 | 候选 | 当前判断 |
| --- | --- | --- | --- |
| P1 | `R7-A` | Boundary-Risk Aware Training | `D4-lite Feasible-B trend`，但正式 D4 必须打过 static aux 2.0 / focal / class-balanced / risk controls |
| P2 | `R7-B` | Branch-to-Final Disagreement Distillation | 当前 D2/D3 teacher/partition 不干净，D3.5 只保留 loss-path 证据，不解锁正式 D4 |
| P3 | `R7-D` | Confidence-Calibrated Auxiliary Curriculum | 当前 sample aux 被 static aux 2.0 打穿，`Not-worth-full-D4 for current lite setup` |
| P4 | `R7-C` | Error-Region Contrastive Boundary Learning | hard-region memory 与 controls 不分离，D3.5 只证明表征路径可达 |

## R7-A：Boundary-Risk Aware Training

核心想法：reliability 不再选择 source 或预测标签，而是决定哪些训练样本需要更强 final-boundary regularization。

候选 loss：

```text
risk(x) = f(final margin,
            branch disagreement,
            confidence uncertainty,
            historical loss volatility,
            modality inconsistency)

L = CE(final, y)
  + lambda1 * risk(x) * MarginLoss(final, y)
  + lambda2 * risk(x) * Consistency(final, branch_ensemble_stopgrad)
  + lambda3 * risk(x) * AntiOverconfidenceLoss
```

核心机制实验：

1. `D2` risk enrichment：用 train/val-only 导出计算 risk，证明 high-risk bin 对错误、低 margin、correct-to-wrong、弱域样本的富集显著超过 random、margin-only、confidence-only、branch-disagreement-only 和 shuffled-risk。
2. `D3` frozen / offline upper bound：只把 risk 作为样本权重或 loss-mask 作用在 train-only small head / calibration proxy 上，检查 risk-weighted hard region 是否比 random-weighted hard region 更能改善 val hard-bin without hurting all-val。
3. `D3.5` gradient sanity：真实 PANDA train batch 上检查 `risk*MarginLoss`、`risk*Consistency`、`risk*AntiOverconfidence` 是否对 final classifier / `h_final` 产生 finite nonzero gradient；报告与 CE 梯度 cosine、risk bin 梯度集中度，并对比 confidence-only、random risk、shuffled risk。
4. `D4-lite` short dynamics：若 D3.5 不退化，跑 1-2 epoch mini-smoke，对比 deterministic、same-budget noop、confidence-only/random/shuffled risk，只看 val trend / flip / hard-bin，不写正式 No-Go。
5. `D4` seed42 smoke：实现 `CE + risk*MarginLoss + risk*Consistency + risk*AntiOverconfidence`，对比 deterministic、same-budget noop、static aux 2.0、focal loss、class-balanced CE、random risk weights、shuffled risk、margin-only risk。
6. `D5` three-seed val：仅当 D4 打过 best control 且 flip 净正时，复核 seeds 2024/2026。

No-Go 作用域：

- 若 D2 risk 不能富集任何 hard/error 区域，只关闭当前 risk 定义，允许重组 risk。
- 若 D3 被 random/shuffled/margin-only 打穿，只关闭当前 offline risk-weighting 变体。
- D3.5 若梯度为 0/NaN、完全等同 CE 或只由 confidence-only control 解释，只关闭当前 loss 公式。
- D4-lite 若短训趋势明显负向，只写 `Not-worth-full-D4 for current lite setup`。
- 只有 D4 primary 低于 deterministic 或输给 focal / class-balanced / static aux / random risk / shuffled risk，才写 `No-Go for current R7-A training implementation`。

当前结果补记：

- D3.5 中 `risk_margin` 触达 final classifier / `h_final`，final cosine `0.985530`、`h_final` cosine `0.937508`，说明它更像 hard/uncertain CE/margin reweighting；`risk_consistency` 与 CE 冲突，`anti_overconfidence` 梯度太弱。
- D4-lite 中 `r7a_composite_risk_lite` 达到 F1/Acc/AUC `0.732329/0.739837/0.866367`，flip vs deterministic `75/18` 净 `+57`，优于 confidence/random/shuffled risk controls。
- 该候选保留为 `D4-lite Feasible-B trend`，但不是正式 D4 成功；若继续，优先重构为更干净的 risk-aware CE/margin weighting，并把 static aux 2.0、focal、class-balanced、confidence/random/shuffled risk 写进 D4 manifest moat。

## R7-B：Branch-to-Final Disagreement Distillation

核心想法：不让 branch 直接投票，而是把 branch agreement / disagreement 转成训练期 teacher signal，最终仍由 final head 学到边界。

候选 loss：

```text
p_branch = aggregate(p_text, p_image, p_fusion)

L = CE(p_final, y)
  + lambda1 * KL(p_final || p_branch_stopgrad) on reliable branch-agreement samples
  + lambda2 * MarginExpand(p_final, y) on branch-disagreement samples
  + lambda3 * SuppressWrongBranch on samples where one branch confidently disagrees with label
```

核心机制实验：

1. `D2` partition validity：验证 branch-agreement-correct、branch-disagreement、single-branch-high-conf-wrong 三类 partition 的 coverage、error enrichment、label correctness、domain distribution 和 low-margin overlap；必须打过 shuffled branch identity、random branch logits、confidence-only partition。
2. `D3` teacher upper bound：在 train/val-only 上比较 vanilla KD、branch ensemble direct prediction、final+aux weighted average、ordinary stacking、agreement-only KD proxy 和 disagreement-margin proxy，确认 teacher partition 不是普通 weighted average 可解释。
3. `D3.5` gradient sanity：检查 agreement-KL、disagreement-margin、wrong-branch-suppression 是否对 final classifier / `h_final` 或 branch feature path 产生有限非零梯度，并与 vanilla KD / ordinary weighted average 梯度比较。
4. `D4-lite` short dynamics：只在 D3.5 不退化时跑 1-2 epoch mini-smoke，观察 teacher loss 是否稳定、是否快速伤害 original final boundary。
5. `D4` seed42 smoke：训练 final-boundary distillation 版本，分别打开 agreement-KL、disagreement-margin、wrong-branch-suppression 三个项，并跑 full primary。
6. `D5` three-seed val：仅当 D4 primary 打过 vanilla KD、static aux 2.0、weighted average / stacking、random teacher、shuffled disagreement 后进入。

No-Go 作用域：

- D2 partition 不成立，只关闭当前 partition 定义。
- D3 被 vanilla KD 或 weighted average 打穿，只关闭当前 teacher construction。
- D4 输给 static aux 2.0 / vanilla KD / random teacher / shuffled disagreement，才关闭当前训练实现。

## R7-C：Error-Region Contrastive Boundary Learning

核心想法：离线 memory 不能直接补 logits，但 hard-region memory 可以在训练期塑造 `h_final`，把低 margin 正负样本拉开。

候选 loss：

```text
M = train samples with low final margin or high branch disagreement

positive = same label + nearby domain/branch profile
negative = different label + similar final representation

L = CE(final, y)
  + lambda * SupCon(h_final, y, hard_region=M)
  + mu * InterClassMargin(h_final)
```

核心机制实验：

1. `D2` hard-region memory audit：只用 train split 建 memory，验证 hard positives / hard negatives 的 label purity、representation similarity、domain/branch profile 匹配度、low-margin overlap；打过 random memory、label-shuffled memory、class-prior memory。
2. `D3` representation upper bound：固定 frozen `h_final` 做 hard-neighbor retrieval / contrastive proxy，只作为可分性上限；若 plain kNN 或 class-prior memory 就能解释，不进入训练 smoke。
3. `D3.5` gradient sanity：检查 hard-region SupCon / InterClassMargin 对 `h_final` 表征的梯度是否 finite/nonzero，是否产生 collapse 风险；final classifier 不直接受该 loss 梯度是设计预期，但必须证明 representation path 可达。
4. `D4-lite` short dynamics：只在 D3.5 不退化时跑 1-2 epoch mini-smoke，观察表示范数、hard-bin、overall 和 flip 是否快速恶化。
5. `D4` seed42 smoke：小 lambda、warmup 后开启 SupCon / boundary contrastive；对比 CE-only、all-sample SupCon、random hard-region SupCon、label-shuffled hard memory、class-prior memory、same-budget longer training。
6. `D5` three-seed val：仅当 D4 hard-bin 与 overall 均不降、flip 净正、且 controls 不可解释时进入。

No-Go 作用域：

- D2 memory 不纯或 hard negative 不存在，只关闭当前 memory 构造。
- D3 被 kNN / class-prior / random memory 解释，只关闭当前 frozen upper-bound。
- D4 过正则导致 overall 下降、hard-bin 不升或被 all-sample SupCon / random memory 打穿，才关闭当前训练实现。

## R7-D：Confidence-Calibrated Auxiliary Curriculum

核心想法：R6-A 显示 aux supervision 强度影响训练动态，但复杂 schedule 未打过 static aux 2.0。下一步不再堆固定 schedule，而是让样本级 branch reliability 决定 aux 权重。

候选 loss：

```text
branch_reliable_b(x) =
  branch confidence moderate/high
  branch agrees with label
  branch not historically overconfident-wrong

L_aux = sum_b w_b(x, epoch) * CE(branch_b, y)
```

权重规则：

- `w_b` 上升：branch 正确且 final uncertain。
- `w_b` 下降：branch overconfident wrong 或与 label 长期冲突。
- `w_b` 上升：模态特异 hard example 且该 branch 提供正确信号。

核心机制实验：

1. `D2` branch reliability audit：按 branch correctness、confidence、final uncertainty、domain/low-margin 分桶，验证“branch correct but final uncertain”是否存在足够 coverage 与 recoverable errors；打过 random branch reliability、shuffled reliability、confidence-only、branch-accuracy-only。
2. `D3` aux-weight proxy：在 train/val-only 日志或 short proxy 中比较 sample-level aux weights 与 static aux weights 的 hard-bin influence，确认不是简单提高 aux loss 总量。
3. `D3.5` gradient sanity：比较 sample-level aux curriculum、static aux 2.0、random/shuffled aux weights 对 branch feature groups、`h_final` 和 final classifier 的梯度触达；若只走 branch 间接路径，必须明确为训练动态证据而非 final-boundary 直接证据。
4. `D4-lite` short dynamics：只在 D3.5 不退化时跑 1-2 epoch mini-smoke，与 static aux 2.0、random/shuffled curriculum 同预算比较。
5. `D4` seed42 smoke：实现 sample-level aux curriculum，对比 deterministic、static aux 2.0、aux sweep、random sample aux weights、shuffled branch reliability、focal loss、same-budget longer training、detached/no-feature-update aux。
6. `D5` three-seed val：仅当 D4 打过 static aux 2.0 且 branch/final flip 净正时进入。

No-Go 作用域：

- D2 没有 recoverable branch-correct/final-uncertain 区域，只关闭当前 reliability rule。
- D3 显示只是在提高 aux 总量，只关闭当前 proxy。
- D4 输给 static aux 2.0、random/shuffled aux weights 或 same-budget longer training，才关闭当前训练实现。

当前结果补记：

- D3.5 中 sample-level aux、static aux 2.0、random/shuffled aux 都不直接触达 final classifier 或 `h_final`，只更新 branch path；sample aux 的 branch 梯度弱于 static aux 2.0。
- D4-lite 中 `r7d_sample_aux_curriculum_lite` F1/Acc/AUC `0.630592/0.660163/0.836594`，低于 static aux 2.0 control `0.736521/0.739837/0.837197`；flip 净收益 `+8` 也低于 static aux 的 `+57`。
- 当前 R7-D sample aux curriculum 降为 `Not-worth-full-D4 for current lite setup`；该结论不是正式训练实现 No-Go，也不永久排除重新定义 reliability rule 的 aux curriculum。

## 晋级与最终主线选择

1. 四个候选都必须完成各自 `D2/D3` 直接机制验证；若某项因 artifact 缺失 `Blocked`，先补 export 或明确 blocker，不得因分析排除。
2. 若某候选 `D2/D3` 可行，标记 `Feasible-A/B` 并继续验证其他候选，不提前封主线。
3. 全部 `D2/D3` 完成后，必须先补 D3.5；若 D3.5 显示 loss 不触达、NaN/0 梯度或完全被简单 control 解释，则只关闭当前 loss 公式。当前 D3.5 已完成。
4. D3.5 通过的候选进入 `D4-lite`，用 1-2 epoch 同预算 mini-smoke 观察训练动态；D4-lite 不产生正式 No-Go，只决定是否值得冻结正式 D4。当前 R7-A/R7-D D4-lite 已完成，只有 R7-A 保留正向趋势。
5. 正式 `D4` 只在 Weibo-21 seed42 train/val-only 执行，强 controls 必须同 budget、同 split、同指标落盘。
6. `D5` 只给 D4 过线候选；三 seed val mean 不低于 deterministic、至少 2/3 seeds Macro-F1/Acc 正向、任一 seed drop 不超过 0.3pp、flip audit 不净负，才可进 `Primary-Candidate`。
7. test 永远只做 confirmatory；不得参与方法选择。

## 当前 TODO 入口

具体执行步骤写入 `todo.md` 的 `P0：Round 7 Risk-Aware Final-Boundary Learning（D2/D3 浅层完成 / D3.5 与 D4-lite 补深度）`。本文件是方法规划与当前 Gate-0/D3.5/D4-lite 记录；未来若正式开训，必须另建 frozen manifest 与 run notes。
