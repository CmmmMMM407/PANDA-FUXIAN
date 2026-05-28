# Round 6 PANDA 方案：Auxiliary-Supervision Rebalancing for Branch-to-Final Alignment

日期：2026-05-26

状态更新（2026-05-28）：本文档是 Round 6 初版 R6-A 细化方案，保留为历史设计记录。Round 6/7 应跑验证已闭环：R6-A 已完成 seed42 train/val-only D4 smoke 并判定当前训练实现 `No-Go`；R6-C 三 seed offline 复核不稳定；R6-D/G/H/J 已补 direct/complementarity/frozen-response probes 并判定当前变体 `No-Go`；R6-B/R6-E/R6-F/R6-I 当前 frozen/offline 变体也已 `No-Go`。当前没有 `Primary-Candidate`；新的待执行规划入口已切到 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md`、`round7_candidate_registry.md` 和 `round7_gate0_manifest_TEMPLATE.json`。

## 定位

Round 6 是 R2/R3/R4/R5 全部未产生 `Primary-Candidate` 之后的新一轮第一性原理候选池。2026-05-26 初版阶段在 protocol 冻结前不训练、不连接远端；2026-05-27 已按用户要求连接云端做只读源码复审，但仍未启动训练，未导出、未打开、未分析 test。后续判断以云端活代码审计、既有 train/val 证据、子代理蓝军审查和候选登记表为准。

本轮主候选暂定：

```text
R6-A: Auxiliary-Supervision Rebalancing for Branch-to-Final Alignment
```

核心边界：

- `aux_weight_2p0` 是新的正信号来源，但它是 R5-A smoke 的 control，不是 R5-A 成功。
- R5-A `image_project` primary 已 No-Go，不能继承到 R6。
- R6-A 已按独立 smoke manifest 完成 seed42 D4 训练验证；当前训练实现 No-Go。
- 未来不得把 static aux/control 现象包装成 R6-A 成功，若重开必须另立新候选或新 manifest。

## No-Go 归因机制矩阵

| 路线 | 结论 | 被 random / shuffled / control 打穿 | 只改善 calibration | correct->wrong 风险 | final boundary 归因 |
| --- | --- | --- | --- | --- | --- |
| R2 P2-A reliability-conditioned final correction | No-Go；primary F1/Acc `0.929841/0.930081`，低于 original `0.956086/0.956098` | 是；random-feature control 校准类支持更强 | 否，primary 校准也变差 | 未在摘要给出 | reliability/uncertainty 直接修 final logit 会破坏已很紧的边界 |
| R2 P2-B reliability adapter | No-Go；reliability primary `0.909821/0.910569` | 是；`adapter_final_aux_residual` control 到 `0.959346/0.959350` | 否 | 未在摘要给出 | reliability adapter 不能入边界；aux-logit 弱信号需另起机制验证 |
| R2 P2-C domain expert | No-Go；true-domain primary `0.951209/0.951220` | 是；random-route same-architecture control 到 `0.957715/0.957724` | 部分校准改善不足以过主指标 | 未在摘要给出 | domain route 没证明优于随机路由，不能解锁真实 9-domain expert training |
| R2 P2-D source utility residual | No-Go；primary `0.951216/0.951220` | 是；`anchor_platt` control `0.954451/0.954472`，shuffled source feature 也接近 | 是；AUC/ECE/HCE 可由 Platt/shuffled 解释 | 摘要未给 | source utility residual 是离线校准/扰动，不是 architecture-level boundary gain |
| R3 Regret Router | No-Go；soft route self-domain collapse | 是；shuffled/regret controls 不支持机制 | 否 | 未见摘要 flip | non-self source utility 被 self prior 压住，effective source 接近 1 |
| R3 branch-boundary residual | No-Go；best primary `0.949593/0.949593` | 是；ordinary combiner `weighted_average_final_aux_logits` 到 `0.956093/0.956098` | 有 ordinary combiner / calibration 风险 | 是；`3 wrong->correct / 7 correct->wrong` | aux/gap residual 没形成净边界收益，被普通 late fusion 解释 |
| R4 first-principle boundary rebuild | R4-A/D/C No-Go；R4-B Diagnostic-only | 是；Platt、class-prior、random/PCA/label-shuffle 等 controls 接近或打穿 | Platt 可改善校准但掉主指标 | 是；A `7/25`，D `5/12`，C `5/16` | 离线 class/prototype/low-rank/memory correction 主要是破坏性扰动 |
| R4 forced source-view / DCA | No-Go | 是；shuffled PAD top2 CE 低于 PAD top2，random/bottom 对照不支持稳定机制 | 否 | 未见摘要 flip | source/prompt 只弱扰动 final logits，不能证明 source knowledge 进边界 |
| R5 Gate-0 G0-A/D/E/S | 诊断完成，但不解锁 R5-Prime/R5-A+D/R5-S | 是；G0-E 低于 original，G0-S 被 shuffled CE 打穿 | 否；G0-D 是 destructive fragility | 是；G0-D `7 wrong->correct / 17 correct->wrong` | Gate-0 只能说明断点，不是方法许可 |
| R5-A image projection | No-Go；primary `0.936504/0.936585` < deterministic `0.938175/0.938211` | 是；`aux_weight_2p0` control `0.939837/0.939837` 打穿 | 部分；ECE/冲突率改善但主指标掉 | 是；`9 wrong->correct / 10 correct->wrong` | 降低 conflict telemetry 不等于提升 final boundary |

压缩后的总归因：

```text
R2-R5 反复说明：
reliability / source / domain / aux / branch 信号能解释错误、改善校准或制造 logit 扰动，
但一旦要求它们稳定改变 final decision boundary，
就会被 random/shuffled/control 解释，或把更多 correct 样本翻成 wrong。
```

## PANDA 模块第一性原理审计

PANDA 当前主路径：

```text
content + image + CLIP inputs
-> frozen BERT / frozen MAE / frozen CN-CLIP
-> text/image/fusion branch experts
-> branch aux heads: p_text, p_image, p_fusion
-> h_di = h_text + h_image + h_fusion
-> domain prototype / PAD / Gumbel top-S selector
-> DCA over static target/source prompts
-> h_collab
-> final_classifier_panda([h_di, h_collab])
-> y_score

training:
BCE(final) + lambda_rec * reconstruction + mean(BCE(text), BCE(image), BCE(fusion))
```

逐模块判断：

| 模块 | 第一性原理功能 | 当前失败机制 | Round 6 可替换方向 |
| --- | --- | --- | --- |
| frozen BERT/MAE/CLIP | 提供基础文本、图像、跨模态表征 | backbone 冻结，错误只能由上层边界修补；CLIP-only conflict 证据不强 | 只作为二阶段：低 margin adapter / LoRA smoke；不能抢 R6-A |
| branch experts | 把 text/image/fusion 压成可监督 branch feature | forward 主要用 index 0 gates/experts，不是真 9-domain MoE | 若重开，必须做真 domain-conditioned adapters + random/domain-shuffle controls |
| aux heads | 给三条 branch 直接监督 | 有诊断信息，但默认只作平均 aux BCE；未显式对齐 final boundary | R6-A 主战场：aux weight、schedule、branch-specific reweight、final-aligned ramp |
| `h_di` branch sum | 融合三条 branch | 裸相加无法表达哪条 branch 可信；冲突可能被平均掉 | R6-C/R6-D 可探索 branch weighting 或 label-preserving modality robustness |
| prototype/PAD/GNS | 建 domain relation 和 neighbor prompts | hard top-k、self prior、source ranking 被 shuffled/random 打穿 | 默认关闭；除非新 Gate-0 证明 sample-conditioned source interaction |
| DCA prompts | late prompt-to-prompt source/domain bias | 不看样本内容，进入 final 太晚 | 只作失败边界证据；不作为 R6 主线 |
| final head | `MLP([h_di,h_collab])` 决策 | 旧信号在 boundary 外或太晚进入 | R6-A 只通过训练期 aux supervision 改写 branch features，不做 late residual |
| loss system | final BCE + rec + aux BCE | aux/final 强度、时序和梯度贡献未系统控制 | R6-A 重新预注册 auxiliary supervision rebalancing |

## 外部方法谱系

本轮只借能解释当前失败规律的方法，不堆模块：

- Deeply-Supervised Nets 表明中间层 companion objectives 可提高中间特征 discriminativeness、robustness 和训练有效性；这支持“aux supervision 可能是结构性抓手”，但不支持事后调权成功叙事。[PMLR: Deeply-Supervised Nets](https://proceedings.mlr.press/v38/lee15a.html)
- GradNorm 将多任务训练问题定义为动态调节各任务梯度幅度；这直接对应 PANDA final BCE 与 text/image/fusion aux BCE 的强度不平衡风险。[arXiv: GradNorm](https://arxiv.org/abs/1711.02257)
- Kendall 等的 uncertainty loss weighting 说明多 loss 相对权重会显著影响多任务系统，手动权重昂贵且不稳；这支持把 `aux_weight_2p0` 升为待验证机制，而非单点调参。[arXiv: Uncertainty Weighting](https://arxiv.org/abs/1705.07115)
- Dynamic Weight Average / MTAN 说明任务权重可按训练速度动态变化；R6-A 的 schedule/ramp 必须与静态 aux sweep 做强对照。[arXiv: MTAN/DWA](https://arxiv.org/abs/1803.10704)
- PCGrad / CAGrad 说明多任务冲突梯度是常见问题；但 R5-A 已显示 generic PCGrad/CAGrad 不自动有效，因此在 R6 中只能作为强对照，不是主创新。[arXiv: PCGrad](https://arxiv.org/abs/2001.06782), [arXiv: CAGrad](https://arxiv.org/abs/2110.14048)
- Calibration literature 说明 temperature/Platt scaling 常能改善 calibration；因此任何只改善 ECE/Brier/HCE 的候选不得升级为主方法。[arXiv: On Calibration](https://arxiv.org/abs/1706.04599)
- SWA/EMA 类训练稳定化可作为第二梯队候选，但若只改善方差或校准，不满足方法主线。[arXiv: SWA](https://arxiv.org/abs/1803.05407)

## Round 6 初版候选池（已被 2026-05-27 登记表扩展）

最新候选编号以 `round6_candidate_registry.md` 为准：

| 最新编号 | 候选 | 备注 |
| --- | --- | --- |
| R6-A | Auxiliary-Supervision Rebalancing | 本文档保留为 R6-A 细化方案 |
| R6-B | Evidence-Gated Branch Aggregation | 新增，最接近 `h_di` final boundary |
| R6-C | Boundary-Local Lightweight Calibration | diagnostic-only unless flip net positive |
| R6-D | Cross-Architecture Disagreement Distillation | 原本文档 R6-B 已改号 |
| R6-E | Deep Supervision / Early-Exit Diagnostic | 新增 |
| R6-F | Label-Preserving Modality Robustness | 原本文档 R6-C 已改号 |
| R6-G | Soft Prototype Memory / EMA Prototype Estimator | 新增 |
| R6-H | Sample-Conditioned Prompt Memory | 新增 |
| R6-I | Domain-Conditioned Final MoE / Low-Rank Boundary Adapter | 新增 |
| R6-J | Differentiable Non-Self Source Mixture | 新增 |

以下小节为初版草案内容，保留作为 R6-A 和历史候选构思记录；后续执行不得直接使用旧编号。

### R6-A: Auxiliary-Supervision Rebalancing for Branch-to-Final Alignment

优先级：P0，第一轮主候选。

第一性原理：

PANDA 的 branch auxiliary heads 已经被 label supervision 直接监督。R2/P2-B 说明 aux logits 包含弱预测 cues；R3 说明 late aux residual 会被 ordinary combiner 打穿；R5-A 说明 image gradient projection 不能把 conflict telemetry 转成 final boundary gain。唯一剩余正信号是 `aux_weight_2p0`：它轻微超过 deterministic，并显著降低 image conflict rate。

因此 R6-A 不再问“能不能把 aux logits 拼进 final”，而问：

```text
auxiliary supervision 的强度、分支配比与训练时序，
能否让 branch features 在训练期更稳定地服务 final boundary？
```

核心假设：

- 默认 `mean(aux BCE)` 的强度/时序不是最优。
- 适度提高或调度 aux supervision 可能比 image projection 更有效。
- 真机制必须同时表现为主指标不低于 deterministic、flip audit 净正、branch conflict telemetry 改善，并打过静态 aux sweep / random aux / shuffled aux controls。

必须降调的点：

- `aux_weight_2p0` 只是 candidate signal。
- R6-A 不能叫 R5-A follow-up，也不能说 image projection 成功。
- 若最佳结果只是某个静态 aux weight，论文主张只能是 auxiliary-supervision sensitivity；不能包装成复杂机制。

历史 Gate-0 设计边界：

1. 数据与 split：Weibo-21 seed42，train/val-only，`test_split_exported=false`，`test_used_for_decision=false`。
2. selector：`deterministic_train`。
3. 训练长度：先只允许 5-epoch smoke；正式 50-epoch 必须在三 seed val 复核后另行预注册。
4. baseline：`deterministic_train_l0`、`same_budget_noop_l0`。
5. primary family：
   - `r6a_static_aux_weight_2p0_confirm`：复现 R5 control，不作为最终方法。
   - `r6a_late_aux_ramp_0p5_to_2p0`：前期弱 aux，后期增强 branch discriminativeness。
   - `r6a_warm_aux_ramp_2p0_to_1p0`：前期强 branch shaping，后期回归 final boundary。
   - `r6a_branch_specific_image2_text1_fusion1`：只验证 image branch 是否是主受益源。
   - `r6a_final_aligned_aux_gate`：只在 aux/final prediction 同向或 low-margin 区间加强 aux。
6. 输出：summary CSV/JSON/MD、manifest、flip audit、gradient telemetry compact、per-domain/weak-domain/HCE summary、checkpoint lifecycle notes。

强对照：

- 静态 aux weight sweep：`0.0/0.5/1.0/1.5/2.0/3.0`。
- random aux labels：只打乱 aux loss label，不动 final label。
- shuffled branch-label mapping：text/image/fusion aux label source 互换或打乱。
- aux loss detached/no-feature update control：检查是否只是额外 loss 数值噪声。
- generic PCGrad/CAGrad/GradNorm 或 DWA 至少两个可实现对照。
- random-sign gradient penalty。
- same-forward-budget / same-epoch control。
- final-only loss + longer epoch control，防止收益来自训练预算。

Go 线：

- primary val Macro-F1/Acc 不低于 deterministic，并优先要求 `>= +0.3pp`。
- primary 必须高于最优静态 aux sweep control；若输给静态 sweep，只能写成 sensitivity，不可写成新方法。
- flip audit 净正：wrong->correct > correct->wrong。
- image/text/fusion conflict telemetry 至少一个关键分支改善，且不能出现主指标下降。
- weak-domain F1、HCE、ECE/Brier 至少两项不劣化。

No-Go 线：

- primary 低于 deterministic。
- primary 不高于 best aux static/control。
- 只改善 ECE/Brier/HCE 或 conflict telemetry，不改善 F1/Acc。
- correct->wrong >= wrong->correct。
- random aux / shuffled branch / same-budget control 同样达到收益。
- seed42 过线但 seed2024 或 seed2026 任一低于 deterministic。

checkpoint 生命周期：

- 所有 R6-A smoke checkpoint 放入可回收目录：`param_model/round6_r6a_smoke/...`。
- No-Go 后删除 checkpoint，只保留 `repro_logs/round6_r6a_smoke/seed*/manifest/summary/flip/telemetry/notes`。
- 只有 R6-A 进入 `Primary-Candidate` 后，才允许长期保留三 seed checkpoint。
- 不同步 checkpoint 到公开日志仓库。

### 初版 R6-B：Cross-Architecture Disagreement Distillation（最新编号 R6-D）

优先级：P0/P1，最本质不同的候选。

假设：PANDA、MMDFND、DAMMFND 已完成两数据集三 seed baseline；若错误互补存在，跨架构 soft teacher 可能比 PANDA 自蒸馏更稳。

Gate-0：

- 先只做 train/val offline complementarity：oracle upper-bound、teacher-student disagreement、teacher correct / PANDA wrong 覆盖率。
- 只有互补超过 random/self-distill 才允许小型 distill smoke。

强对照：PANDA self-distill、temperature-only、random teacher、shuffled teacher logits、single-teacher DAMMFND/MMDFND。

No-Go：互补不超过随机或自蒸馏；提升只被 calibration 解释；teacher 需要 test 选择。

### 初版 R6-C：Label-Preserving Modality Robustness（最新编号 R6-F）

优先级：P1。

假设：final boundary 对某模态过表达敏感，但不能重写 CLIP conflict 因果线。

Gate-0：

- 同样本内 text-drop/image-drop/fusion-drop，验证 view 真实扰动 logits 且 full-view F1/Acc 不塌。
- 训练只允许 label-preserving consistency，不做跨样本图文替换。

强对照：普通 dropout、random mask same-rate、R-Drop、label smoothing、mask schedule shuffle、same-forward-budget。

No-Go：普通 dropout 同样有效；full-view 主指标下降；branch reliance collapse；consistency 抹掉真假新闻有效冲突 cue。

### R6-D: Conditional Domain-Nuisance Control

优先级：P1/P2。

假设：R4-B 证明 domain 可线性解码，但直接去域会伤 label；只能压制同 label 内与错误相关的 domain nuisance。

Gate-0：

- train-only conditional domain probe：验证 `domain | label` 是否预测 val error/low-margin/weak-domain。
- 同时报告 label probe / class margin 是否保持。

强对照：domain-label shuffle、random partition、unconditional adversary、GroupDRO/REx/Fishr、domain one-hot calibration。

No-Go：conditional domain-error AUC 不显著；domain probe 降了但 F1/Acc 掉；random partition 同样有效。

### R6-E: Temporal Stability / EMA-SWA Boundary Training

优先级：P2。

假设：多轮失败暴露 seed sensitivity 和 boundary flips；训练轨迹稳定化可能比新 selector 更有效。

Gate-0：deterministic_train 下比较 last/best/EMA/SWA/snapshot consistency，固定 epoch 和 forward budget。

强对照：extra epoch、random snapshot averaging、weight averaging with shuffled epochs、label smoothing、SAM。

No-Go：收益来自多训练或 best-checkpoint 选择；只改善校准/方差。

### R6-F: Risk-Controlled Selective PANDA

优先级：Fallback，不作为主方法优先。

假设：若全覆盖 F1 难提升，选择性预测可作为风险控制论文角度。

Gate-0：只用 val 固定 coverage/risk 阈值，报告 risk-coverage、HCE reduction、weak-domain coverage。

强对照：max-confidence threshold、temperature scaling、Platt、random abstention、domain-only abstention。

No-Go：被 max-confidence 或 Platt 完全解释；coverage 太低；不能服务主任务指标。

### R6-G: Stable-Error / Label-Noise Robust Training

优先级：P2。

假设：跨 seed/跨模型稳定高置信错误可能是歧义或噪声样本。

Gate-0：离线统计 stable hard errors，只用 train/val；再跑 GCE/SCE/bootstrap loss 小 smoke。

强对照：focal loss、hard-example mining、random downweight、shuffled hard-error mask、class-prior mask。

No-Go：stable-error 集合不稳定；downweight 后主指标下降；random mask 同样有效。

## Round 6 状态机

```text
Protocol-Draft
-> Frozen-Gate0
-> Running-Gate0
-> No-Go / Feasible-A / Feasible-B
-> All-Candidates-Gated
-> Deep-Validation
-> Primary-Candidate
-> Three-Seed-Val
-> Confirmatory-Test
```

强制规则：

1. Protocol-Draft 阶段不跑任何实验。
2. 每个候选必须先写 Gate-0、controls、No-Go、checkpoint lifecycle。
3. 候选 Gate-0 失败时按 `level_reached` 落状态并切换：`D0/D1` 不写 No-Go，`D2/D3` 只关闭当前 frozen/offline/proxy 变体，`D4` 才关闭当前训练实现。
4. 候选可行只能标 Feasible-A/B；必须继续验证其他候选。
5. 所有活跃候选赛完后，才允许选择 Primary-Candidate。
6. 三 seed val 过线前，不导出、不打开、不分析 test。
7. 任何 seed42 smoke 不能越级成为主线。

2026-05-28 收口状态：

- Round 6/7 当前应跑验证已完成闭环，但未产生 `Primary-Candidate`。
- R6-A 已在 `round6_r6a_smoke_manifest.json` / `FROZEN_SMOKE` 约束下完成 seed42 D4 smoke，当前训练实现 `No-Go`。
- R6-C 的 seed42 `Feasible-B` 弱正信号经 seeds 2024/2026 复核后不稳定，只保留 low-margin diagnostic。
- R6-D/G/H/J 的误杀风险补实验已完成，当前 direct/complementarity/frozen-response 变体均 `No-Go`。

## 首轮执行建议

首轮执行建议已执行完毕并收口；以下只保留为历史编号对照，不再是待办命令。若未来重新提出本质不同的新候选，必须另起 protocol/manifest，而不是沿本文档旧编号续参：

1. R6-A：auxiliary supervision rebalancing protocol。
2. R6-B：evidence-gated branch aggregation Gate-0。
3. R6-C：boundary-local lightweight calibration diagnostic Gate-0。
4. R6-D：cross-architecture complementarity offline Gate-0。
5. R6-F：modality robustness view-delta Gate-0。

历史要求中“冻结后开 seed42 smoke”的前提已被后续协议修正并执行：`round6_r6a_gate0_manifest.json` 只是非训练 Gate-0 manifest；后续已另建 `round6_r6a_smoke_manifest.json` 并冻结为 `FROZEN_SMOKE`，完成 seed42 smoke 后判定当前 R6-A 训练实现 `No-Go`。未来若重开，必须另立本质不同的新 manifest，并显式记录：

- `allowed_splits=["train","val"]`
- `test_split_exported=false`
- `test_used_for_decision=false`
- `primary_family`
- `control_family`
- `go_rule`
- `no_go_rule`
- `checkpoint_lifecycle`
- `promotion_rule`

## 当前结论

Round 6 的最小可写主张不是“R5-A 终于成功”，而是：

```text
PANDA 的 source/domain/reliability/late-aux 信号没有稳定进入 final boundary。
R6-A 将唯一剩余正信号 aux_weight_2p0 重新定义为
auxiliary supervision strength/schedule 的独立候选，
并用强对照检验它是否能训练期对齐 branch features 与 final boundary。
```

当前 Round 6/7 应跑验证已闭环但没有可升主线证据；R6-A 当前 D4 训练实现已 No-Go，不进入三 seed val、不扩 Weibo、不看 test。
