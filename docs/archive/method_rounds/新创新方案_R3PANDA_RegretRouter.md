# R3-PANDA 新创新方案：Regret-Regularized Reliable Routing

日期：2026-05-25

## 当前状态：已冻结 / No-Go

2026-05-28 更新：本文档继续作为历史 No-Go 记录保留。当前项目已越过历史 R4、Round 2、Round 3、Round 4 first-principle、Round 5 Gate-0、R5-A smoke 和 Round 6/7 当前作用域验证；新的待执行规划入口为 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 与 `round7_candidate_registry.md`。

2026-05-25 Weibo-21 seed42 5-epoch gate 已完成，R3-PANDA MVP 判定为 No-Go。所有正向 R3 variants 的 val F1/Acc 未超过 deterministic strong control，并且出现完全 self-domain route collapse：`r3_effective_source_num_mean≈1.000006`、`r3_self_top1_ratio=1.0`、non-self alpha 约 `1e-7`。因此本文件保留为历史方案和失败边界记录，不再作为当前执行路线。

当前新候选路线为 `R4-PANDA: Non-self Source-domain Intervention Consistency`，详见 `新创新方案_R4PANDA_CounterfactualConsistency.md`。R4 也只是候选，必须先过 frozen-view validity gate；不能把 R3 失败结果反向包装成 R4 成功证据。

## 一句话判断

旧 selector 路线失败，不是因为 reliability / uncertainty 信号没有价值，而是因为它只改变了 PAD/Gumbel 的离散邻居集合，缺少“源域是否真的帮助当前样本分类”的训练闭环。

新方法主线应从：

```text
which neighbor is similar?
```

转为：

```text
which source actually reduces supervised risk under this sample/domain condition?
```

推荐方法名：

```text
R3-PANDA: Regret-Regularized Reliable Routing for Prototype-driven Neighbor-domain Adaptation
```

推荐论文题目：

```text
From Similarity to Utility: Regret-Regularized Reliable Neighbor Adaptation for Multimodal Fake News Detection
```

中文题目：

```text
从相似度到效用：面向多模态假新闻检测的后悔正则化可靠邻域迁移方法
```

题目中的 `Reliable` 只作为当前内部候选。最终论文命名必须由 gate 决定：

- 若 reliability vector 相比 no-reliability / random / overconfidence control 有明确贡献，可使用 `Regret-Regularized Reliable Routing`。
- 若主要收益来自 regret，而 reliability vector 无贡献，应改为 `Regret-Regularized Source Utility Routing`。
- 若只有 soft router 有效而 regret 无贡献，不能硬写 regret 为主贡献。

## 第一性原理

PANDA 的核心假设是：

```text
PAD prototype similarity high -> source domain transferable -> select source prompts -> improve target prediction
```

我们当前实验已经给出几个反例或边界：

- CLIP-only conflict 对错误几乎随机，不能作为主因果。
- confidence / fusion uncertainty 能预测错误，但直接改 neighbor logits 不能稳定改善 F1/Acc。
- held-checkpoint control grid 中，即使大量改变 neighbor set，最终标签也常常不变。
- Gumbel selector 会传导到 prediction-level 方差；deterministic 可消除方差，但不等于新方法提升。
- winning control 在 seed2024 明确失败，说明单点不确定性门控容易 seed-sensitive。

因此，新方法必须满足四个条件：

1. 路由是可微的，梯度能影响表示与最终分类边界。
2. 源域选择不再只由 prototype similarity 决定，而要由 supervised utility / negative transfer regret 约束。
3. reliability 信号不直接监督 error label，只作为 router 和鲁棒训练的条件变量。
4. 方法必须同时报告 overall、weak-domain、reliability、stability 和 routing mechanism。

## 方法核心

R3-PANDA 包含三个主模块和两个可选扩展。

### A. Soft Source Utility Router

替换 PANDA 的 Gumbel top-S neighbor selector。对每个样本和每个候选 source domain 计算连续路由权重：

```text
alpha_i,s = softmax((pad_logit_i,s + router_mlp([h_i, e_t, e_s, r_i])) / tau)
```

其中：

- `pad_logit_i,s` 来自 PANDA 原始 PAD similarity。
- `h_i` 是 PANDA 的 `h_di = h_text + h_image + h_fusion`。
- `e_t`、`e_s` 是 target/source domain embedding。
- `r_i` 是 detached reliability vector，例如 branch disagreement、fusion uncertainty、confidence uncertainty。
- `tau` 从高温到低温退火，先探索再收敛。

这一步的重点不是“又一个 attention”，而是把原本离散、随机、弱传导的 source selection 变成可微的 source utility routing。

### B. Source Adapter Residuals and Candidate Source Logits

旧 PANDA 中 neighbor prompts 进入 DCA 后，有时对 final logits 影响太弱。R3-PANDA 给每个 source 增加轻量残差 adapter：

```text
a_i,s = Adapter_s(h_i)
h_collab_i,s = mean(DCA(prompt_target_i, prompt_source_s))
z_i,s = FinalHead([h_i + a_i,s, h_collab_i,s])
```

主预测使用 soft routed feature：

```text
h_route_i = h_i + sum_s alpha_i,s * a_i,s
c_route_i = sum_s alpha_i,s * h_collab_i,s
z_i = FinalHead([h_route_i, c_route_i])
```

这样 route 权重不只改变 neighbor set，而是直接改变 source residual、collaborated prompt feature 和 final classifier input。

实现起步配置：

```text
adapter_dim = 64
router_hidden = 128
tau_start = 2.0
tau_end = 0.7
candidate_sources = all domains
self/target domain kept as target-only anchor
```

### C. Negative Transfer Regret Loss

这是 R3-PANDA 的关键闭环。

对每个候选 source，计算它相对 target-only anchor 是否让训练损失变差：

```text
regret_i,s = CE(y_i, z_i,s) - CE(y_i, z_i,self)
```

若 `regret_i,s > 0`，说明 source s 对当前样本是潜在负迁移。惩罚 router 给它高权重：

```text
L_neg = mean_i sum_s alpha_i,s * relu(stopgrad(regret_i,s) + margin)
```

关键约束：

- 只用 train label，不用 val/test error label。
- regret 本身 stop-gradient，先让它作为 utility target，避免训练初期互相追逐。
- source candidate logits 与主预测共享 final head，确保 regret 与最终分类边界同构。
- target-only anchor 是每个样本自己的 domain route，不是额外 oracle。

这比旧 reliability selector 更强，因为它直接问：

```text
这个 source 是否让监督分类损失变差？
```

而不是只问：

```text
这个 source 的不确定性均值是否接近当前样本？
```

### D. Group-Robust Outer Loss

为了防止 router 只服务强域，加入轻量 group risk regularization。第一版不直接上复杂 meta-learning，先用 batch 内 domain risk variance 或 GroupDRO-style reweighting：

```text
L_group = Var_g( mean_{i in g} CE(y_i, z_i) )
```

group 建议按优先级：

1. domain
2. domain x label
3. domain x uncertainty-bin
4. val-defined weak-domain vs non-weak-domain

如果 batch 内 domain 太稀疏，先用 domain risk EMA 或只在每个 epoch 统计更新 group weights。

### E. Reliability / Evidence Extension

若 R3-PANDA 的 classification gate 过线，但 reliability 指标仍不够强，再接 Evidential Multi-Branch Heads：

```text
e_m = softplus(W_m h_m)
alpha_m = e_m + 1
u_m = K / sum(alpha_m)
```

其中 `m in {text, image, fusion}`。这条线借鉴 evidential learning 和 trusted multi-view classification，把 text/image/fusion 分支从普通概率变成 evidence + uncertainty。

第一轮不建议把 evidence head 放进 MVP，原因是 PANDA 已经很重，新变量太多会拖慢 gate 判断。

## 总目标函数

第一版 MVP：

```text
L = L_cls
  + L_aux
  + lambda_rec * L_rec
  + lambda_neg * L_neg
  + lambda_bal * L_balance
```

第一轮 gate 暂不把 group loss 放进主判断。先验证 `soft router + source adapter + L_neg` 是否形成机制闭环；若 MVP 过线，再把 group loss 作为 second-stage robustness extension。否则一旦失败，很难判断是 regret、group reweighting 还是二者耦合导致。

第二版 full：

```text
L = L_cls
  + L_aux
  + lambda_rec * L_rec
  + lambda_neg * L_neg
  + lambda_group * L_group
  + lambda_route * L_route_cons
  + lambda_bal * L_balance
  + lambda_cal * L_brier
```

初始网格：

```text
lambda_neg:   [0.01, 0.03, 0.05]
lambda_bal:   [0.001, 0.005]
lambda_group: [0.0, 0.01]
lambda_route: [0.0, 0.01]
margin:       [0.0, 0.02]
adapter_dim:  [64]
tau_start:    2.0
tau_end:      [0.7, 1.0]
```

## 与 R2-PANDA 的关系

R2-PANDA 的方向是 soft prompt-adapter neighbor adaptation，核心已经对；但 R3-PANDA 更明确地把主创新压到一个可检验命题上：

```text
prototype similarity is not enough; source utility should be learned through regret.
```

因此建议 R3-PANDA 作为新主线，R2-PANDA 作为历史草案或模块库。

## 快速 Gate

先跑 Weibo-21 seed42 5-epoch gate，不碰 test 做选择。

### Baselines

- PANDA Gumbel short5
- deterministic eval short5
- deterministic train short5
- old winning control short5

### R3-PANDA Variants

1. `regret_soft_pad_only`
   - 只用 softmax PAD logits 替代 Gumbel，不加 reliability、不加 adapter、不加 regret。
   - 目的：确认 soft route 本身可稳定训练和评估。
2. `regret_soft_adapter_l0`
   - 加 source adapter residual，`lambda_neg=0`。
   - 目的：排除纯路由改写无效，确认 route perturbation 能影响 final logits。
3. `regret_soft_adapter_neg`
   - 加 `L_neg`。
   - 目的：验证 negative transfer regret 是否带来 val F1/Acc 非退化和 route-regret 机制闭环。
4. `regret_soft_adapter_neg_reliability`
   - 在 router 输入中加入 reliability vector。
   - 目的：只在它超过 no-reliability 时，才允许论文主张 reliable routing。
5. `regret_soft_adapter_neg_balance`
   - 加很小的 balance / entropy 约束。
   - 目的：只用于防 route collapse，不作为第一贡献。
6. `regret_soft_adapter_neg_group`
   - 二阶段扩展，不进入 MVP 主判断。

### Negative Controls

- no reliability vector in router
- random reliability vector
- overconfidence vector
- shuffled regret within batch
- `lambda_neg = 0`
- adapter without soft route
- adapter-only with comparable parameter count
- PAD-only soft router without reliability

### Gate 通过线

必须同时满足：

1. Val Macro-F1 / Acc 不低于 deterministic reference，理想提升 >= 0.3 个点。
2. Weak-domain Macro-F1 不退化。
3. AUC、ECE、Brier、HCE 至少两个改善。
4. `corr(alpha_i,s, -regret_i,s)` 为正，说明 router 真在回避高 regret source。
5. Route entropy 不塌缩到单一 source；load balance 或 source diversity 有合理范围。
6. Route perturbation 会改变 final logits，而不只是改变日志里的 neighbor set。
7. random / overconfidence / shuffled-regret control 不能取得同等收益。

必须额外导出 route collapse 诊断：

- `alpha_mean_per_source`
- `effective_source_num = exp(entropy(alpha))`
- `self_route_ratio`
- `top1_source_frequency`
- `route_entropy_by_domain`

若 seed42 过线：

- 立刻跑 Weibo-21 seeds 2024/2026。
- seed2024 是关键反例复核，必须不重演旧 winning-control 失败。
- 三 seed val mean 不低于 deterministic，且至少 2/3 seeds 的 Macro-F1 / Acc 不退化，才允许扩 Weibo。
- final test 只做 confirmatory，不允许根据 test 结果回头改 `lambda_neg`、`tau`、`adapter_dim` 或 reliability 配方。
- Weibo-21 三 seed 过线后，才解锁 Weibo。

若 seed42 不过线：

- 先看 soft router 是否比 hard Gumbel 稳定。
- 若 F1 不升但 ECE/Brier/HCE 大幅改善，转向 trustworthy / selective PANDA。
- 若连 reliability 指标也不改善，No-Go，不进入正式方法主表。

## 论文结构设想

RQ1: Is prototype similarity sufficient for reliable neighbor-domain adaptation?

RQ2: Can source-level regret guide soft neighbor routing and reduce negative transfer?

RQ3: Does reliability information improve routing beyond random, overconfidence, and PAD-only controls?

RQ4: Does R3-PANDA improve weak-domain performance, calibration, and prediction stability?

贡献写法：

1. We identify a similarity-utility gap in prototype-driven neighbor-domain adaptation.
2. We propose a differentiable source utility router with source adapters and counterfactual candidate source logits.
3. We introduce negative transfer regret regularization to penalize harmful source routing without using validation/test error labels.
4. We provide mechanism diagnostics linking route weights, source regret, weak-domain behavior, and calibration.

## 主要风险

1. PANDA baseline 很强，F1 提升可能小；必须同时准备 weak-domain、HCE、ECE/Brier 和 route-regret correlation 证据。
2. `L_neg` 用 train label，可能被质疑过拟合；需要 stop-gradient、warmup、small lambda、seed2024 复核和 shuffled-regret control。
3. `regret` 可能被审稿人误解为训练标签驱动的后验路由。写作时应称为 supervised negative transfer regularization，明确不用 val/test error tuning，也不用 `is_error` 监督。
4. source adapters 增加参数；必须报告参数量，并做 adapter-only / no-adapter / lambda_neg=0 消融。
5. soft router 可能塌缩到 target/self domain；需要 `self_route_ratio`、`effective_source_num`、`alpha_mean_per_source` 和 entropy 诊断，但 balance 权重要小，避免强行平均。
6. 如果 evidence head、selective prediction 和 group loss 一起上，方法会显得堆模块；第一轮只做 R3 core，group/evidence/selective 都作为二阶段扩展。

## 可借鉴文献

- PANDA / Prototype-driven Asymmetric Neighbor-Domain Adaptation: https://ojs.aaai.org/index.php/AAAI/article/view/37049
- GroupDRO / worst-group robustness: https://arxiv.org/abs/1911.08731
- DomainBed / DG 方法稳定性警示: https://arxiv.org/abs/2007.01434
- MLDG / episodic domain generalization: https://arxiv.org/abs/1710.03463
- VREx / risk variance: https://arxiv.org/abs/2003.00688
- Fishr / gradient variance alignment: https://arxiv.org/abs/2109.02934
- Soft MoE / differentiable expert routing: https://arxiv.org/abs/2308.00951
- AdapterFusion: https://arxiv.org/abs/2005.00247
- Evidential Deep Learning: https://arxiv.org/abs/1806.01768
- Trusted Multi-View Classification with Dynamic Evidential Fusion: https://arxiv.org/abs/2204.11423
- SelectiveNet / selective prediction: https://arxiv.org/abs/1901.09192
