# Round 2 PANDA 方法候选池：Final-Boundary First

日期：2026-05-26

## 定位

状态说明（2026-05-28 更新）：本文档仍只作历史 Round 2 gate 记录。Round 6/7 当前作用域验证已闭环且无 `Primary-Candidate`；新的待执行规划入口为 Round 7 `Risk-Aware Final-Boundary Learning`，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 和 `round7_candidate_registry.md`。验证深度复审后，本文所有 No-Go 必须按作用域读取：P2-A/P2-B/P2-C/P2-D 主要是 `D3` offline/frozen 变体结论，不能永久排除训练期 domain MoE、differentiable source mixture 或全新 final-boundary training mechanism。

状态说明（2026-05-26 更新，2026-05-27 复审后按 D-level 重读）：Round 2 已完成并关闭。P2-A、P2-C、P2-D 是当前 D3 offline/frozen 变体 No-Go；P2-B reliability adapter 是当前 D3 offline adapter No-Go；无 reliability 的 `final+aux logits` residual adapter 曾保留为 `Feasible-B` 弱信号，但 Round 3 强对照复核后已降级为 current D3 offline ordinary-combiner risk evidence。本文档保留为历史 gate 记录；Round 3、Round 4、Round 5 Gate-0 与 R5-A 单项 smoke 后仍无 `Primary-Candidate`，R5-A 已因 primary 低于 deterministic 且被 `aux_weight_2p0` control 打穿而 `No-Go for current image projection training implementation`。当前论文目标仍是方法性论文，不是诊断型报告；diagnostic/report 草稿、reliability/uncertainty 分析和所有 No-Go 证据只作为方法动机、强对照和 fallback。

Round 2 的核心原则：

```text
不要再只改 neighbor set 或 source prompt。
先证明新模块能进入 final classifier boundary，
再谈 source-domain adaptation 或 reliability-aware learning。
```

## 失败规律复盘

1. 只改 PAD/Gumbel selector 不够。
   - 大量 neighbor set 改变不等于 final label 改变。
   - Held-checkpoint reranking 基本不改变 Macro-F1/Acc。

2. Reliability/uncertainty 是强信号，但旧用法不稳。
   - confidence-uncertainty 能解释错误、高置信错误和弱域。
   - 但 selector / reliability extension 的三 seed val F1/Acc 不稳，seed2024 是强负例。

3. R3 说明 learned source router 会 self-collapse。
   - non-self alpha 接近 0。
   - regret/source utility 没有进入 final classifier boundary。

4. R4/P0-B/P1-A 说明 source-view/PAD ranking 对 final logits 影响弱。
   - forced source views 有非零微扰，但 PAD top2 被 shuffled/random/bottom controls 打穿。
   - feature-aware ranking 改变 source set，但不能证明 ranking 本身有效。

5. P1-B 说明“domain gate 修复”不能直接写成方法。
   - 当前 checkpoint 不是 9-domain gate/expert groups。
   - index1 扰动是 unused task branch control，不是 domain-conditioned evidence。

## Round 2 候选顺序

### P2-A：Reliability-conditioned Final-Boundary Correction

状态：`No-Go for current D3 offline reliability-conditioned final-logit correction`（2026-05-26）；训练期 reliability/final-boundary mechanism 需新 manifest + D4。

最小 gate 结果：original final score val F1/Acc `0.956086/0.956098`；best reliability-conditioned correction `final_plus_aux_reliability_domain` 只有 `0.929841/0.930081`，ECE/Brier/HCE/weak-domain F1 也全面变差；best random-feature control 在校准类支持指标上更强。结论是当前 train-fitted offline correction 特征集会破坏 PANDA reproduced final boundary，不能作为该 claim_scope 的方法主线；这不排除训练期 loss/representation/final-boundary 机制重新设计。

主命题：

```text
如果可靠性/不确定性信号确实解释错误，
但 selector 路径不能稳定传导到 final boundary，
那就先直接检验这些信号能否修正 final logits boundary。
```

最小 gate：

- 不训练 PANDA 主模型。
- 只用 train 拟合 correction，val 决策。
- 输入候选特征：
  - original final logit / score。
  - `p_text`、`p_image`、`p_fusion`。
  - branch disagreement、fusion uncertainty、confidence uncertainty、overconfidence。
  - category/domain one-hot 或 domain bias。
  - PAD / neighbor fields 只作为消融，不作为第一贡献。

强对照：

- 原始 final logit。
- temperature scaling / Platt scaling。
- domain-bias-only。
- aux-logits-only。
- random-feature controls。
- shuffled reliability controls。

Go 条件：

- train 拟合、val 决策，不碰 test。
- val Macro-F1/Acc 不低于 deterministic。
- 至少一个主指标有清晰提升，且不是 calibration-only 能解释。
- ECE/Brier/HCE/weak-domain 至少两个方向改善。
- random/shuffled controls 不能同样达到。

No-Go 条件：

- 只改善 AUC/ECE/Brier，不改善或损害 Macro-F1/Acc。
- domain-bias-only 或 temperature/Platt control 同样有效。
- random/shuffled reliability control 同样有效。

### P2-B：Lightweight Final Head / Boundary Adapter

状态：`No-Go for current D3 reliability/source-utility adapter`；`Feasible-B` weak signal for aux-logit residual boundary adapter（2026-05-26）。

最小 smoke 结果：best reliability primary `adapter_final_reliability_residual` val F1/Acc `0.909821/0.910569`，明显低于 original final score `0.956086/0.956098`，因此不能写成 reliability-aware adapter 成功。无 reliability 的 `adapter_final_aux_residual` 达到 `0.959346/0.959350`，weak-domain F1 `0.948029`，提示 text/image/fusion auxiliary logits 可能含有 final head 未显式消费的 predictive cues；若后续回到该信号，必须把该方向重新定义为 Round 3 branch-boundary residual 候选，并补三 seed、parameter-matched、random-feature、calibration-only、ordinary-combiner 与 branch-drop controls。

主命题：

```text
如果离线 final-boundary correction 有信号，
下一步用冻结 PANDA 表征或 logits 训练极小 adapter，
验证一个可训练边界模块能否稳定吸收 reliability/source-utility 信息。
```

最小 gate：

- 冻结 PANDA backbone。
- 只训练一个很小的 final-head adapter 或 logit residual。
- 第一版不加大模块，不改主干。
- 先 batch smoke，再 Weibo-21 seed42 5-epoch。

强对照：

- deterministic eval/train。
- calibration-only。
- parameter-matched MLP，不输入 reliability/source fields。
- random-feature adapter。
- duplicate-head control。

Go 条件：

- seed42 val F1/Acc 不低于 deterministic。
- 机制字段显示 adapter residual 不是常数 bias。
- parameter-matched MLP 和 random-feature adapter 不能同样达到。

No-Go 条件：

- 提升来自纯 bias / calibration。
- 训练 adapter 过拟合 train，val 不稳。
- 与 random-feature adapter 无差异。

### P2-C：Actual Domain-conditioned Expert Modules

状态：`No-Go` for offline pre-screen（2026-05-26）。

蓝军反审后将该 gate 明确降级为 `P2-C-offline-final-boundary-smoke`，不能直接算完整 9-domain expert module 成功。已补入 per-domain Platt、shared + domain one-hot、parameter-matched shared、sample-shuffle、uniform random route、prior-matched random route 与 random-feature controls。结果：true-domain 9-expert residual val F1/Acc `0.951209/0.951220`，低于 original `0.956086/0.956098`；same-architecture `random_route_domain_expert_seed2` control 达到 `0.957715/0.957724`。因此不解锁基于当前 offline pre-screen 的结构训练；真实训练期 9-domain MoE 仍为 `Not-Unlocked`，若重开需新增 modules、shape/backward sanity、parameter-matched/random-domain/domain-shuffle controls，并达到 D4。

主命题：

```text
如果 PANDA 源码中的 expert/gate 不是实际 9-domain 条件化，
那只能通过新增真实 domain-conditioned modules 来验证这个方向，
不能用 index1 控制分支冒充 domain gate。
```

最小 gate：

- 明确新增 9-domain text/image/fusion 或 final-boundary expert modules。
- 先做结构 smoke：shape、strict load 兼容、forward/backward finite。
- 先小参数版本，不直接堆大 MoE。

强对照：

- parameter-matched shared expert。
- random domain routing。
- domain-shuffle routing。
- index1 unused branch control。

Go 条件：

- source/domain expert 对 final logits 有稳定贡献。
- val 指标不低于 deterministic。
- parameter-matched/shared/random controls 不能同样解释。

No-Go 条件：

- 只是参数更多导致提升。
- domain-shuffle 同样有效。
- 训练不稳定或特定 seed 崩。

### P2-D：Architecture-level Source-Utility Reorganization

状态：`No-Go` for offline influence gate（2026-05-26）。

复用 R4 forced-view train/val 长表构造 PAD top2 non-self source residual 特征。Anchor baseline val F1/Acc `0.956086/0.956098`；best source residual `source_utility_top2_residual` 为 `0.951216/0.951220`，虽然 AUC/ECE/HCE 有改善，但主指标下降，且 `anchor_platt` 与 shuffled source feature controls 能解释校准收益。status_scope 为 `No-Go for current D3 PAD-top2 source residual offline influence gate`；不解锁该 source-utility residual training，也不排除 self-suppressed / differentiable non-self source mixture 另立候选。

主命题：

```text
如果 PAD/DCA/source prompt 作为前置装饰太弱，
就不要继续补丁式改 selector，
而要把 source utility residual 放进 final classifier boundary 内部。
```

最小设计：

```text
h_di -> self logit
h_di + source_utility_residual -> source-conditioned logit
rho_i -> self/source boundary mixing
final logit = (1-rho_i) * z_self + rho_i * z_source
```

最小 gate：

- 先做 frozen/offline influence gate，确认 source residual 不会被 final head 吃掉。
- 再做 batch smoke。
- 最小训练只用 seed42 5-epoch。

强对照：

- source residual random。
- shuffled utility。
- self-only residual。
- parameter-matched residual MLP。
- old winning control。

Go 条件：

- source utility residual 明确影响 final logits。
- val F1/Acc 不低于 deterministic，最好有 >=0.3pp 提升。
- weak-domain 或 high-uncertainty bin 有同步改善。
- controls 不能同样达到。

No-Go 条件：

- rho 塌缩到 self 或常数。
- source residual 被 random/shuffled controls 打穿。
- 只改善校准，不改善主指标。

## 历史执行纪律

1. P2-A -> P2-B -> P2-C -> P2-D 顺序固定。
2. 任一候选核心逻辑未达标时，按 `level_reached` 落状态：`D0=Evidence-only/Provisional`，`D1=Blocked`，`D2/D3=No-Go for current probe/offline/frozen variant`，`D4=No-Go for current training implementation`，`D5=stability conclusion`。
3. 任一候选先可行，只标记 `Feasible-A/B`，继续验证剩余候选。
4. 全部候选赛完后，再对可行候选做三 seed val 深入复核。
5. 三 seed val 没过线前，不导出、不打开、不分析 test。
6. 每轮都必须做蓝军反审：源码链路、方法创新、实验门控、审稿风险。

## 历史主线判断与当前承接

Round 2 的第一优先不是“再找一个更聪明的 selector”，而是先回答：

```text
有没有一种轻量、可解释、强对照打不穿的方式，
让可靠性/源域效用真正进入 PANDA 的最终分类边界？
```

Round 2 的实际结果表明：当前 D3 offline 版本的 reliability、domain routing 与 source utility 接入方式不稳。P2-B `final+aux logits` residual adapter 曾承接到 Round 3 Branch-Boundary Residual，但 Round 3 已证明当前 D3 offline aux-logit / branch-gap residual 不能在 ordinary-combiner moat 下成立。R3-D training-time endogenous residual 仍是 `Not-Unlocked`，若重开需新 manifest + D4；历史上后续进入 Round 4 first-principle boundary rebuild。
