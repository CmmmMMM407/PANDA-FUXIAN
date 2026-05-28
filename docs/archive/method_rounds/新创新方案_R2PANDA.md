# R2-PANDA 新创新方案

日期：2026-05-25

状态说明（2026-05-28 更新）：本文档已完全归档为历史方案。Round 6/7 当前作用域验证已闭环且无 `Primary-Candidate`；新的待执行规划入口为 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 和 `round7_candidate_registry.md`。

状态说明（2026-05-26 更新，2026-05-27 复审后按 D-level 重读）：本文档保留为历史方法构思记录。后续 R3/历史 R4/P0-B/P1-A/P1-B/P1-C、Round 2 P2-A/P2-B/P2-C/P2-D，以及 Round 3 branch-boundary residual 的 gate 已进一步证明，仅靠 selector/routing/source-view/reliability/source-utility/aux-logit residual 侧修改难以稳定进入 final classifier boundary。但这些结论只关闭已跑的当前实现、frozen/probe/offline 变体或当前训练实现；P1-B、R5 reserve、P2-E、soft/EMA prototype、训练期 domain MoE、全新 non-self mixture 等未达到对应 D4/D5 的方向不得被永久排除。当时执行主线曾转向 `新创新方案_Round4PANDA_FirstPrincipleBoundary.md`，该线现也已完成并归档为 scope-limited No-Go / Diagnostic-only。

## 核心判断

旧 selector 路线失败的根因不是“没有可靠性信号”，而是：

```text
reliability signal 有效，但只改 PAD/Gumbel top-S 邻域重排，无法稳定传导到 final classifier boundary。
```

因此新方法不再主打 reliability-aware selector，而是把可靠性信号接入训练闭环、路由机制和表示鲁棒性。方法论文应重新定位为：

```text
Reliability-Regularized Soft Prompt-Adapter Neighbor Adaptation
```

内部简称：

```text
R2-PANDA
```

候选英文题目：

```text
Reliability-Regularized Soft Prompt-Adapter Neighbor Adaptation for Multimodal Fake News Detection
```

候选中文题目：

```text
面向多模态假新闻检测的可靠性正则化软提示-适配器邻域迁移方法
```

## 第一性原理

PANDA 原始机制有三层：

1. 用 domain prototypes 计算邻域相似度。
2. 用 Gumbel top-S 选邻域 domain prompts。
3. 用 DCA 把 target prompt 和 neighbor prompts 融合进最终分类。

我们观察到：

- CLIP-only conflict 不强，不能当主因果。
- branch disagreement、fusion uncertainty、confidence-uncertainty 能预测错误。
- 但仅靠 reliability score 改 neighbor logits，哪怕改变大量 neighbor set，也常常不改最终标签。
- Gumbel selector 会带来 prediction-level 方差；deterministic 稳定但不构成新方法收益。
- Weibo lambda=0.0 是边界条件，说明“手写 re-ranking”很容易失效。

所以新方法要满足：

1. 路由必须可微、可训练、能影响 final logits。
2. 可靠性信号不能监督 `is_error`，只能控制学习方式。
3. 负迁移必须被训练目标显式惩罚，而不是只事后诊断。
4. 方法要能报告 overall、weak-domain、reliability、robustness 四类收益。

## 方法总览

R2-PANDA 包含四个模块。

### 模块 A：Soft Neighbor Prompt Router

把 PANDA 的 hard top-S neighbor selection 改成 soft neighbor prompt fusion。

原 PANDA：

```text
PAD sim -> Gumbel top-S neighbor domains -> DCA(target prompt, selected neighbor prompts)
```

R2-PANDA：

```text
PAD logits + h_di + domain embedding + detached reliability features
    -> soft router alpha_i,s
    -> weighted neighbor prompt collaboration
```

形式：

```text
alpha_i = softmax(MLP([h_i, domain_emb_i, PAD_logits_i, r_i]) / tau)
h_collab_i = sum_s alpha_i,s * DCA(prompt_i, prompt_s)
```

训练早期用高温度 soft routing，后期退火到低温度或 top-k sparse routing。这样 router 有连续梯度，不再依赖 Gumbel 离散噪声。

### 模块 B：Prompt Bank + Lightweight Source Adapters

PANDA 现在每个 domain 只有一组 prompt，表达太粗。R2-PANDA 扩展为：

```text
prompt_bank[D, R, 3*Lp, Dp]
```

每个 domain 有 R 个子 prompt expert。第一版 R=2，避免参数膨胀。

同时在 `h_di` 或 `h_collab` 后增加小型 source adapters：

```text
z_s = Adapter_s(h_di)
h_route = h_di + sum_s beta_i,s * z_s
```

直觉：

- prompt bank 解决 domain 内混合新闻模式。
- adapter fusion 给每个 source 一个可被抑制的残差通道，比只改 prompt 更容易影响 final logits。

### 模块 C：Negative Transfer Regret Loss

这是新方案最关键的闭环。

对每个 source adapter / prompt route，估计它是否让当前样本训练损失变差：

```text
regret_i,s = CE(y_i, pred_with_source_s) - CE(y_i, pred_target_only)
```

若某个 source 带来正 regret，说明它对当前样本是潜在负迁移。惩罚 router 给它高权重：

```text
L_neg = mean_s alpha_i,s * relu(regret_i,s + margin)
```

注意：

- 只用 train label，不用 val/test error label。
- `pred_with_source_s` 可以用轻量 source-specific adapter head 近似，避免每个 source 完整 forward。
- regret 用 stop-gradient 版本起步，防止训练不稳定。

它的语义不是“预测错误检测”，而是“source 对监督目标是否有害”。这比旧 reliability prototype 更直接。

### 模块 D：Reliability-Regularized Multimodal Robustness

可靠性信号不再用来直接改 selector，而是控制训练方式。

可用 detached reliability：

```text
branch_disagreement = |p_text - p_image|
fusion_uncertainty = 1 - |2*p_fusion - 1|
confidence_uncertainty = 1 - |2*mean(p_text,p_image,p_fusion) - 1|
r_i = normalize(branch_disagreement + fusion_uncertainty)
```

四个正则：

1. Route consistency  
   同一样本两次 dropout / weak augmentation 后，路由分布应稳定。

```text
L_route_cons = KL(alpha_i^1 || alpha_i^2) + KL(alpha_i^2 || alpha_i^1)
```

2. Load balance  
   防止 router 永远选少数 source/prompt。

```text
L_balance = KL(mean_batch(alpha) || Uniform)
```

3. Reliability-weighted cross-modal contrastive  
   低不确定样本拉近 text/image/fusion 表示；高不确定样本不强行当 hard positive。

```text
L_con = (1 - r_i) * InfoNCE(text_i, image_i)
```

4. Modality dropout consistency  
   训练时随机 mask/noise text 或 image branch，要求完整预测与扰动预测不要剧烈翻转。

```text
L_mod_cons = KL(p_full || p_masked) * w_i
```

其中 `w_i` 可对低中不确定样本更强，对极高不确定样本较弱，避免错误强约束。

## 总训练目标

第一版建议：

```text
L = L_cls
  + L_aux
  + lambda_rec * L_rec
  + lambda_neg * L_neg
  + lambda_route * L_route_cons
  + lambda_bal * L_balance
  + lambda_con * L_con
  + lambda_mod * L_mod_cons
```

默认初始网格：

```text
lambda_neg:   [0.01, 0.05]
lambda_route: [0.01]
lambda_bal:   [0.005, 0.01]
lambda_con:   [0.01, 0.05]
lambda_mod:   [0.01]
tau_start:    2.0
tau_end:      0.5
prompt_R:     2
adapter_dim:  64
```

训练 schedule：

1. Epoch 1 warmup：只开 `L_cls + L_aux + L_rec`，soft router 高温。
2. Epoch 2-3：开 `L_balance + L_route_cons`。
3. Epoch 4 后：开 `L_neg + L_con + L_mod_cons`。
4. 若 5-epoch gate 稳定，再做 50-epoch paper-aligned run。

## 为什么这比旧方案更可能成功

旧方案：

```text
可靠性信号 -> 改 neighbor logits -> selected neighbors 变化 -> final label 经常不变
```

新方案：

```text
可靠性信号 -> 控制训练正则 / 软路由 / adapter 残差 / 负迁移损失 -> final representation 和 classifier boundary 改变
```

关键差异：

- Soft router 有梯度，避免 Gumbel 随机性。
- Adapter 残差通道能直接影响 final logits。
- Negative transfer regret 用监督损失定义 source 是否有害。
- Reliability 不再只是错误相关特征，而是控制 contrastive、consistency、modality robustness。

## 快速 Gate 实验

先只做 Weibo-21 seed42 5-epoch 小网格。

### Baselines

- PANDA Gumbel short5
- deterministic eval short5
- deterministic train short5
- old winning control short5

### Variants

1. `soft_router`
2. `soft_router + route_cons + balance`
3. `soft_router + prompt_bank(R=2)`
4. `soft_router + adapter_fusion`
5. `soft_router + adapter_fusion + L_neg`
6. `soft_router + adapter_fusion + L_neg + reliability_contrastive`
7. full R2-PANDA

### Negative Controls

- random reliability weight
- overconfidence weight
- CLIP-only weight
- fusion-only
- branch-only
- no reliability feature in router

### Gate 通过线

必须同时满足：

1. Val Macro-F1 / Acc 不低于 deterministic eval，最好提升 >= 0.3 个点。
2. AUC、ECE、Brier、HCE、weak-domain F1 至少两个指标改善。
3. Weak-domain F1 不退化。
4. Route entropy / route consistency 明显优于 Gumbel。
5. Route 或 adapter 权重变化能引起 final logits 变化，而不只是 neighbor set 变化。
6. Random / overconfidence control 不能同样提升。

如果 seed42 通过：

- 跑 Weibo-21 seeds 2024/2026。
- 三 seed val mean 必须不低于 deterministic。
- seed2024 不能重演旧 winning-control 反例。
- 再考虑扩 Weibo。

## 备用路线

如果 R2-PANDA 5-epoch 不过线，优先试两个轻量路线：

### Evidence-Calibrated PANDA

把 text/image/fusion/final 输出改成 evidence head，学习 Dirichlet evidence 和 uncertainty。高 branch disagreement / fusion uncertainty 样本降低 evidence，而不是强行改类别。

适合主打 reliability / HCE / calibration，如果 F1 不升但 ECE/Brier 大幅改善，可作为可信分类方法。

### Risk-Coverage Selective PANDA

加 selection head `g(x)`，学习自动判或拒判。目标是 risk-coverage，而不是全覆盖 F1。

适合安全应用叙事，但如果投传统方法论文，需要小心贡献形式。

## 论文叙事

如果 R2-PANDA 成功，论文主线可以写成：

```text
PANDA proves neighbor-domain adaptation is strong, but hard stochastic neighbor selection is unstable and reliability signals do not automatically close the performance loop.
We propose R2-PANDA, a reliability-regularized soft prompt-adapter neighbor adaptation framework.
Instead of using reliability signals to re-rank neighbors post hoc, R2-PANDA injects reliability into differentiable routing, negative-transfer regret, and multimodal robustness training.
```

贡献：

1. Soft prompt-adapter neighbor routing：从 hard Gumbel top-S 变为可微软邻域协作。
2. Negative transfer regret loss：显式惩罚有害 source 路由。
3. Reliability-regularized multimodal training：用 branch/fusion uncertainty 控制 contrastive、consistency 和 modality robustness。
4. 系统实验证明 overall、weak-domain、reliability、stability 多维收益。

## 主要风险

1. 参数变多，PANDA 已经很重。第一版必须 R=2、adapter_dim=64、freeze 大 backbone。
2. Router 可能学 domain prior，要做 leave-one-domain 或 domain-held sanity。
3. `L_neg` 可能过拟合 train label，要小权重、stop-gradient、warmup 后开启。
4. Contrastive 可能强行对齐本来不一致的图文，要 reliability-weighted，不能把高不确定样本当 hard positive。
5. 如果只改善 ECE/Brier/HCE、不改善 F1/Acc，论文要转可信决策叙事，而不是强方法主表。

## 可借鉴文献

- GroupDRO / worst-group robustness：Sagawa et al., Distributionally Robust Neural Networks for Group Shifts.
- DomainBed：In Search of Lost Domain Generalization.
- MLDG：Meta-Learning for Domain Generalization.
- Soft MoE：From Sparse to Soft Mixtures of Experts.
- Expert Choice Routing：Mixture-of-Experts with Expert Choice Routing.
- AdapterFusion：Non-Destructive Task Composition.
- Trusted Multi-View Classification with Dynamic Evidential Fusion.
- OGM-GE：Balanced Multimodal Learning via On-the-fly Gradient Modulation.
- Robust Contrastive Learning Against Noisy Views.
- SelectiveNet / selective prediction.
- Evidential Deep Learning.
- Conformal prediction for classification.
