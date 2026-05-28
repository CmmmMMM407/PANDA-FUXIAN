# Round 7 候选登记表

日期：2026-05-28

状态：`D4-LITE TRENDS RECORDED / FULL-D4 NOT-UNLOCKED / NO-PRIMARY-CANDIDATE`。Round 7 是 R6-A 到 R6-J 当前作用域闭环后的新候选池，不继承 R6 的 `No-Go` 结论，只继承强对照、验证深度规则和 train/val-only 禁令。2026-05-28 已完成 train/val-only artifact audit、R7-A/R7-B/R7-C/R7-D 当前 D2/D3 Gate-0、真实 batch `D3.5 Gradient-Sanity`，并对 R7-A/R7-D 补完 `D4-lite Training-Dynamics-Smoke`。当前未运行正式 5-epoch R7 D4，未导出或分析 test。

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

当前结论摘要：

- Artifact audit `PASS`：train/val rows `4926/615`；final logits / score / margin / per-sample CE、branch probabilities/logits、`h_text/h_image/h_fusion/h_di/h_collab/h_final`、domain/category、branch disagreement、confidence uncertainty 和弱域定义均可用；historical loss volatility 为 `missing_optional`。
- `R7-A`：D2 `Feasible-B` for current composite risk enrichment；D3 `No-Go for current risk-weighted offline proxy at D3`。
- `R7-B`：D2 `No-Go for current branch partition definitions at D2`；D3 `No-Go for current teacher construction at D3`。
- `R7-C`：D2 `No-Go for current hard-region memory construction at D2`；D3 `No-Go for current hard-region frozen memory proxy at D3`。
- `R7-D`：D2 `No-Go for current branch reliability rule at D2`；D3 `No-Go for current aux-weight proxy at D3`。
- D3.5 已完成：R7-A risk-margin 触达 final classifier / `h_final` 但与 CE 高度同向；risk-consistency 与 CE 冲突；R7-B agreement-KD 触达 final boundary 但 D2/D3 teacher 不干净；R7-C contrastive path 触达 `h_final` 但 hard-region 与 all-sample/random controls 不分离；R7-D aux curriculum 只走 branch path，不直接触达 final classifier / `h_final`。
- D4-lite 已完成：R7-A composite risk 短训 F1/Acc/AUC `0.732329/0.739837/0.866367`，优于 deterministic-lite 与 confidence/random/shuffled risk controls，标为 `D4-lite Feasible-B trend`；R7-D sample aux `0.630592/0.660163/0.836594` 明显低于 static aux 2.0 control `0.736521/0.739837/0.837197`，标为 `Not-worth-full-D4 for current lite setup`。

这些结论不解锁正式 D4，也不关闭本质不同的训练期方法族；D3.5/D4-lite 只能作为梯度可达性和短训趋势证据，不能写当前训练实现 No-Go 或 Primary。

主线命名：

```text
Risk-Aware Final-Boundary Learning for Multimodal Multi-Domain Fake News Detection
```

核心要求：

```text
风险信号必须在训练期塑造 final decision boundary；
不能作为推理期 selector、source router、offline adapter 或校准后处理来补救。
```

## 不得 No-Go 规则

- 不得裸写 `No-Go`，必须写成 `No-Go for current <claim_scope> at D<n>`。
- `D0/D1` 不得 No-Go。统计分析、日志解读、源码推断、旧结果类比、接口不通，只能写 `Evidence-only / Blocked / Provisional`。
- `D2/D3` 只允许关闭当前 direct probe、offline/frozen/proxy 变体；不得否定训练期方法族。
- 未跑真实训练 smoke 的训练期方法，不得判“当前训练实现 No-Go”。
- “不解锁 D4 / 不启动训练 / 不抢资源”不是方法失败。
- R4/R5/R6 的旧 `No-Go` 不得跨 `claim_scope` 继承给 Round 7。
- `[x]` 只能表示记录、审计或计划落盘完成，不能自动表示技术假设已验证。

## 共用字段

| 字段 | 含义 |
| --- | --- |
| `candidate_id` | 稳定候选编号 |
| `family` | 方法家族 |
| `hypothesis` | 第一性原理假设 |
| `code_path` | 预期实现或导出挂点 |
| `minimal_mechanism_probe` | D2/D3 核心机制实验 |
| `gradient_sanity` | D3.5 真实 batch forward/backward 梯度 sanity |
| `lite_training_smoke` | D4-lite 1-2 epoch 短训趋势实验 |
| `training_smoke` | D4 训练实验要求 |
| `expected_signal` | 应观察到的核心证据 |
| `primary_baseline` | 主要基线 |
| `strong_controls` | random/shuffled/same-budget/ordinary-method controls |
| `gate_inputs` | 允许使用的数据和 artifacts |
| `forbidden_inputs` | 禁止输入 |
| `metrics` | 指标与审计项 |
| `go_rule` | Feasible-A/B 判定线 |
| `no_go_rule` | 当前 claim_scope 的 No-Go 线 |
| `claim_scope` | 当前候选结论覆盖范围 |
| `level_reached` | 当前最高验证深度 |
| `required_level_for_exclusion` | 排除当前 claim_scope 的最低深度 |
| `status_scope` | 状态边界 |
| `promotion_rule` | 晋级 D4/D5/Primary 的规则 |
| `reopen_condition` | 重开条件 |

## R7-A

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R7-A` |
| `family` | Boundary-risk aware training |
| `hypothesis` | reliability、branch conflict、low margin、weak-domain 不是推理期选择器，而是训练期风险权重；只在高风险区域加强 final margin、final-branch consistency 和 anti-overconfidence，可能让 final boundary 更宽。 |
| `code_path` | `model/PANDA.py::Trainer.train` final CE / aux loss 组合；risk 导出脚本读取 final/branch logits、margin、domain、历史 loss telemetry；未来 manifest 固定 train/val-only。 |
| `minimal_mechanism_probe` | `D2` risk enrichment + `D3` risk-weighted offline/sample-weight proxy；必须比较 random risk、shuffled risk、margin-only、confidence-only、branch-disagreement-only。 |
| `gradient_sanity` | `D3.5`：真实 PANDA train batch 上检查 `risk*MarginLoss`、`risk*Consistency`、`risk*AntiOverconfidence` 对 final classifier / `h_final` 的有限非零梯度、与 CE 梯度 cosine、risk-bin 梯度集中度；比较 confidence-only、random、shuffled risk。 |
| `lite_training_smoke` | `D4-lite`：Weibo-21 seed42 1-2 epoch train/val-only mini-smoke；只比较趋势，不写正式 No-Go。 |
| `training_smoke` | `D4` Weibo-21 seed42 5-epoch：`CE + risk*MarginLoss + risk*Consistency + risk*AntiOverconfidence`，含 ablation。 |
| `expected_signal` | high-risk bin 富集错误/低 margin/correct-to-wrong/弱域，且 D4 primary 的 final F1/Acc、flip audit、hard-bin 指标优于 deterministic 与 strong controls。 |
| `primary_baseline` | deterministic train/eval、original final、same-budget noop。 |
| `strong_controls` | static aux 2.0、focal loss、class-balanced CE、random risk、shuffled risk、margin-only risk、confidence-only risk、same-budget longer training。 |
| `gate_inputs` | Weibo-21 train/val final logits、branch logits/features、domain、margin、per-sample loss；无 test。 |
| `forbidden_inputs` | test split、test-derived threshold/weak-domain、用 val/test error label 训练 risk predictor。 |
| `metrics` | Macro-F1/Acc/AUC、NLL/ECE/Brier/HCE、wrong->correct/correct->wrong、low-margin/weak-domain/hard-risk bins、risk enrichment AUC/odds ratio、control moat。 |
| `go_rule` | D2/D3 risk 非随机且 hard-region 有上限收益；D4 primary 不低于 deterministic，理想 `>= +0.3pp`，flip 净正，并打过 focal/class-balanced/static aux/random/shuffled controls。 |
| `no_go_rule` | D2 只可关闭当前 risk 定义；D3 只可关闭当前 offline proxy；D4 若低于 deterministic或输给 best control，才写当前训练实现 No-Go。 |
| `claim_scope` | 当前 composite risk definition 与 risk-weighted offline logistic proxy；不覆盖重新定义 risk 或训练期 regularization。 |
| `level_reached` | `D4-lite Training-Dynamics-Smoke`；D2 risk enrichment 为 `Feasible-B`，D3 offline proxy No-Go，D3.5 梯度可达但部分项退化/冲突，D4-lite 呈正向趋势。 |
| `required_level_for_exclusion` | 当前训练实现至少 `D4`；稳定性结论至少 `D5`。 |
| `status_scope` | `D4-lite Feasible-B trend / Full D4 Not-Unlocked`；若进入正式 D4，必须打过 static aux 2.0、focal/class-balanced、confidence/random/shuffled risk 等强 controls。 |
| `promotion_rule` | 只有重新冻结正式 D4 manifest 且预注册强 controls 后，才允许 seed42 5-epoch smoke；D4 过线后才进 D5。 |
| `reopen_condition` | 若当前 risk 定义失败，可重新定义 risk 并从 D2 开始；不得外推到所有 risk-aware training。 |

## R7-B

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R7-B` |
| `family` | Branch-to-final disagreement distillation |
| `hypothesis` | branch 分歧可暴露 final boundary 危险区；不让 branch 直接投票，而是把 branch agreement / disagreement 转成训练期 teacher signal，让 final head 内生学习。 |
| `code_path` | branch logits/features 导出；`Trainer.train` 中 final KL、margin expand、wrong-branch suppression loss；branch teacher stopgrad。 |
| `minimal_mechanism_probe` | `D2` partition validity：branch-agreement-correct、branch-disagreement、single-branch-high-conf-wrong；`D3` teacher upper-bound 对比 vanilla KD、ordinary stacking、weighted average。 |
| `gradient_sanity` | `D3.5`：agreement-KL、disagreement-margin、wrong-branch-suppression 与 vanilla KD / ordinary weighted average 的梯度范数、cosine、触达路径对比。 |
| `lite_training_smoke` | `D4-lite`：仅 D3.5 不退化时跑 1-2 epoch mini-smoke，观察 teacher loss 是否快速伤害 final boundary。 |
| `training_smoke` | `D4` Weibo-21 seed42：`CE + agreement-KL + disagreement-margin + wrong-branch-suppression`，逐项 ablation。 |
| `expected_signal` | branch agreement partition 有可靠 teacher value，disagreement partition 对 final hard/error region 有覆盖，D4 final 结果不能被 ordinary branch averaging 解释。 |
| `primary_baseline` | deterministic final、original equal-sum、vanilla KD、自蒸馏。 |
| `strong_controls` | final+aux weighted average、ordinary stacking、static aux 2.0、random branch teacher、shuffled branch disagreement、label smoothing、temperature KD。 |
| `gate_inputs` | train/val branch logits/features、final logits、labels、domain；无 test。 |
| `forbidden_inputs` | test teacher selection、用 test correctness 选择 teacher/temperature/partition。 |
| `metrics` | final F1/Acc/AUC、partition coverage、teacher-correct/final-wrong recoverable coverage、flip audit、hard-bin gains、KL/margin diagnostics。 |
| `go_rule` | D2 partition 非随机且 teacher complementarity 存在；D4 primary 打过 vanilla KD、weighted average、static aux 2.0、random/shuffled teacher。 |
| `no_go_rule` | D2 只关闭当前 partition；D3 只关闭当前 teacher construction；D4 输给 ordinary KD/stacking/static aux 后，才关闭当前训练实现。 |
| `claim_scope` | 当前 branch agreement/disagreement partition definitions 与 branch-teacher offline construction；不覆盖重新定义 teacher 或训练期 distillation。 |
| `level_reached` | `D3.5 Gradient-Sanity`；D2/D3 partition/teacher No-Go，D3.5 只证明部分 loss path 可达。 |
| `required_level_for_exclusion` | 当前训练实现至少 `D4`；稳定性结论至少 `D5`。 |
| `status_scope` | `No-Go for current branch partition definitions at D2 and current teacher construction at D3 / D3.5 path evidence only / Full D4 Not-Unlocked`。 |
| `promotion_rule` | D2/D3 过线后写 smoke manifest；D4 打过 ordinary controls 后进入 D5。 |
| `reopen_condition` | 若 partition 失败，可重设 branch reliability/teacher aggregation，从 D2 重开。 |

## R7-C

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R7-C` |
| `family` | Error-region contrastive boundary learning |
| `hypothesis` | 离线 memory 不能直接补 logits，但 hard-region memory 可以在训练期塑造 `h_final`，把低 margin 正负样本拉开。 |
| `code_path` | train-only hard memory 构造；`model/PANDA.py` final representation `h_final`；SupCon / InterClassMargin loss。 |
| `minimal_mechanism_probe` | `D2` hard-region memory audit；`D3` frozen representation upper-bound / hard-neighbor retrieval proxy；不得用 val/test error label 选 memory。 |
| `gradient_sanity` | `D3.5`：hard-region SupCon / InterClassMargin 对 `h_final` 表征路径的有限非零梯度、collapse 风险和 all-sample/random controls。 |
| `lite_training_smoke` | `D4-lite`：仅 D3.5 不退化时跑 1-2 epoch mini-smoke，观察 hard-bin、overall、embedding norm 和 flip 趋势。 |
| `training_smoke` | `D4` Weibo-21 seed42：小 lambda、warmup 后开启 hard-region SupCon / boundary contrastive + InterClassMargin。 |
| `expected_signal` | hard positives/negatives 有 label purity 与边界可分性；D4 hard-bin 和 overall 均不降，flip 净正。 |
| `primary_baseline` | deterministic CE-only、original final。 |
| `strong_controls` | all-sample SupCon、plain kNN、random hard memory、label-shuffled memory、class-prior memory、final-only calibration、same-budget longer training。 |
| `gate_inputs` | train split 构造 memory；val 只评估；frozen `h_final`、domain/branch profile、labels；无 test。 |
| `forbidden_inputs` | val/test error label 选 region；test-derived memory/hard threshold；把 kNN 后处理写成训练方法。 |
| `metrics` | final F1/Acc/AUC、hard-region F1、embedding separation、intra/inter class distance、representation collapse audit、flip audit、memory purity。 |
| `go_rule` | D2 memory 纯度/coverage 成立；D3 不能被 random/class-prior/kNN 解释；D4 不伤 overall 且 hard-bin 净正。 |
| `no_go_rule` | D2 只关闭当前 memory 构造；D3 只关闭当前 frozen proxy；D4 过正则、overall 降、hard-bin 不升或被 SupCon/random memory 打穿，才关闭当前训练实现。 |
| `claim_scope` | 当前 train-only low-margin/high-disagreement hard memory 与 frozen `h_final` kNN upper-bound proxy；不覆盖重新定义 memory 或训练期 contrastive loss。 |
| `level_reached` | `D3.5 Gradient-Sanity`；D2/D3 memory/proxy No-Go，D3.5 只证明 representation path 可达但 hard-region 特异性不足。 |
| `required_level_for_exclusion` | 当前训练实现至少 `D4`；稳定性结论至少 `D5`。 |
| `status_scope` | `No-Go for current hard-region memory construction at D2 and frozen memory proxy at D3 / D3.5 path evidence only / Full D4 Not-Unlocked`。 |
| `promotion_rule` | D2/D3 明确有 hard-region 上限后才写 D4 manifest；D4 过线后 D5。 |
| `reopen_condition` | 若 low-margin memory 失败，可尝试 high-disagreement/high-loss memory，但必须从 D2 重开。 |

## R7-D

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R7-D` |
| `family` | Confidence-calibrated auxiliary curriculum |
| `hypothesis` | R6-A 的固定 aux schedule 没打过 static aux 2.0，但 branch reliability 可能支持样本级 aux curriculum，使 branch 正确信号在 final uncertain 区域更早进入 final boundary。 |
| `code_path` | `Trainer.train` aux BCE 权重；branch reliability telemetry；sample-level aux weights。 |
| `minimal_mechanism_probe` | `D2` branch reliability audit：branch correct but final uncertain coverage / recoverable errors；`D3` aux-weight proxy，证明不是简单提高 aux 总量。 |
| `gradient_sanity` | `D3.5`：sample-level aux curriculum、static aux 2.0、random/shuffled aux weights 对 branch feature groups、`h_final` 和 final classifier 的梯度触达与 cosine 对比。 |
| `lite_training_smoke` | `D4-lite`：仅 D3.5 不退化时跑 1-2 epoch mini-smoke，对比 static aux 2.0、random/shuffled curriculum。 |
| `training_smoke` | `D4` Weibo-21 seed42：sample-level `L_aux = sum_b w_b(x, epoch) CE(branch_b,y)`，含 reliability rule ablation。 |
| `expected_signal` | branch-correct/final-uncertain 区域存在可恢复错误；D4 打过 static aux 2.0，且 final flip 净正，不只是 ECE/Brier 改善。 |
| `primary_baseline` | deterministic、R6-A static aux sweep、static aux 2.0。 |
| `strong_controls` | random sample aux weights、shuffled branch reliability、confidence-only reliability、branch-accuracy-only、focal loss、same-budget longer training、detached/no-feature-update aux。 |
| `gate_inputs` | train/val branch logits/probabilities、final score、branch correctness on train labels、domain/low-margin bins；无 test。 |
| `forbidden_inputs` | test-derived branch reliability、用 val/test error label 训练 curriculum、事后把 static aux 2.0 包装成 primary。 |
| `metrics` | final F1/Acc/AUC、branch metrics、aux loss distribution、hard-bin / weak-domain gains、flip audit、calibration、same-budget cost。 |
| `go_rule` | D2 recoverable region 充分；D4 primary 打过 static aux 2.0、random/shuffled curriculum 和 same-budget longer training。 |
| `no_go_rule` | D2 只关闭当前 reliability rule；D3 只关闭当前 proxy；D4 输给 static aux 2.0 或 random/shuffled curriculum，才关闭当前训练实现。 |
| `claim_scope` | 当前 branch-correct/final-uncertain reliability rule 与 sample-level aux-weight offline proxy；不覆盖重新定义 reliability rule 或训练期 aux curriculum。 |
| `level_reached` | `D4-lite Training-Dynamics-Smoke`；D2/D3 reliability/aux proxy No-Go，D3.5 显示只走 branch path，D4-lite 被 static aux 2.0 打穿。 |
| `required_level_for_exclusion` | 当前训练实现至少 `D4`；稳定性结论至少 `D5`。 |
| `status_scope` | `Not-worth-full-D4 for current lite setup / Full D4 Not-Unlocked`；这不是当前训练实现 No-Go，也不关闭重新定义 reliability rule 的 aux curriculum。 |
| `promotion_rule` | D2/D3 证明不是 aux 总量效应后才写 smoke manifest；D4 打过 static aux 2.0 后 D5。 |
| `reopen_condition` | 若 branch reliability rule 失败，可重设 rule 或 branch subset，从 D2 重开。 |

## Round 7 晋级矩阵

| 阶段 | 所有候选共同条件 | 输出 |
| --- | --- | --- |
| Artifact Audit | train/val artifacts 足够；缺失则补 export 或 `Blocked` | artifact manifest |
| D2 | 核心机制直接作用到 risk/partition/memory/aux-weight，并打 random/shuffled controls | direct-mechanism summary |
| D3 | train/val-only offline/frozen/proxy upper bound；不能用 test | offline gate summary |
| D3.5 | 真实 PANDA train batch forward/backward 梯度 sanity；候选 loss 必须 finite/nonzero，并报告与 CE/controls 的关系 | gradient sanity summary |
| D4-lite | 1-2 epoch train/val-only mini-smoke，同 budget 强 controls；只看趋势 | lite training dynamics summary |
| D4 | seed42 5-epoch smoke，强 controls 同 budget，落盘 metrics/flip/telemetry | current training implementation Go/No-Go |
| D5 | seeds 42/2024/2026 val 复核；test 仍锁定 | Primary-Candidate ranking |

当前 D2/D3、D3.5 与 R7-A/R7-D D4-lite 已完成：R7-A 仅保留 `D4-lite Feasible-B trend`，R7-D 当前 sample aux 降为 `Not-worth-full-D4 for current lite setup`，R7-B/R7-C 只保留 D3.5 loss-path 证据。四个候选均未解锁正式 D4。若未来重开，仍按 `R7-A -> R7-B -> R7-D -> R7-C` 的优先级，但必须先提出本质不同的新 risk / teacher / memory / curriculum 定义或为 R7-A 冻结更严格的 D4 manifest，不得继承当前 proxy/lite 结论为方法族失败。
