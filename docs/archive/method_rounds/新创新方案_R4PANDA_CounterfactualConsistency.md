# R4-PANDA 新创新方案：Non-self Source-domain Intervention Consistency

日期：2026-05-25

状态更新（2026-05-28）：本文档是历史 R4 source-view 路线记录。Round 6/7 当前作用域验证已闭环且无 `Primary-Candidate`；新的待执行规划入口为 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 和 `round7_candidate_registry.md`。验证深度复审后，本文的 R4 结论只否定当前 `D2` PAD-top2 forced-view / immediate-training 变体，不永久排除全新 self-suppressed non-self source mixture 或本质不同训练期 source protocol。

状态更新：2026-05-26 frozen-view validity gate 已完成，R4 当前判定为 **No-Go for current PAD-top2 forced-view immediate training**。forced non-self source views 能产生非零微扰，但 PAD top2 不能干净打过 bottom/random/shuffled controls；尤其 shuffled PAD top2 在 val CE 上优于 PAD top2。因此当前不冻结 `r4_gate_config.yaml`，不实现 R4 训练开关，不跑 seed42 primary training gate，不复核 seeds 2024/2026，不扩 Weibo。本文件保留为候选方案与失败边界记录，后续只可把 R4 写成 weak intervention-sensitivity diagnostic / failed current source-domain intervention consistency variant。历史上 R4 No-Go 后曾切换到 Round 2；Round 2、Round 3、Round 4 first-principle、Round 5 Gate-0、R5-A 单项 smoke 与 Round 6/7 当前作用域验证现均已完成且没有 `Primary-Candidate`。截至 2026-05-28，新的规划入口是 Round 7 `Risk-Aware Final-Boundary Learning`。

## 一句话判断

R3-PANDA 暂停，不继续在当前 self-domain soft router 上调 `lambda`、group loss 或 reliability vector。R3 的失败暴露出一个更清楚的问题：只要方法仍然把“是否迁移”和“选哪个 source”交给一个会自然偏向 self domain 的路由器，模型就很容易绕开外部邻域迁移。

R4 的新路线改为：

```text
不再先学一个 source router，而是显式构造 non-self source-domain intervention views，
直接训练 final classifier 在外部源域干预下保持分类稳定。
```

推荐方法名：

```text
R4-PANDA: Non-self Source-domain Intervention Consistency for Reliable Neighbor-domain Adaptation
```

推荐论文题目。当前先用克制命名，避免强因果反事实包装：

```text
Counterfactual-Style Non-self Domain Consistency for Neighbor-domain Adaptation in Multimodal Fake News Detection
```

中文题目：

```text
面向多模态假新闻检测邻域迁移的非自身源域干预一致性方法
```

R4 曾是新的候选方法路线，不能提前写成成功方法。执行顺序必须是：先做 frozen-checkpoint forced-view validity gate；只有 validity 通过，才冻结 `r4_gate_config.yaml` 并进入 Weibo-21 seed42 5-epoch primary gate。实际执行结果为 validity 未解锁训练，因此后续 primary gate 关闭。

总控补充：本方案受 `创新方案赛马总控与实施协议.md` 约束。即使 R4 先通过 frozen-view validity，也只能先标记为 `Feasible-A`，继续完成 DCA/source-view risk、feature-aware PAD、domain gate、evidential/reliability extension 等候选的最小可行性验证。所有候选赛完后，才允许把 R4 或其他方案升级为最终 `Primary-Candidate`。

术语红线：正式写作中不使用 `causal counterfactual`、`solves negative transfer` 或 `guarantees reliable transfer`。最多表述为 `counterfactual-style source-domain intervention` 或 `model-internal non-self source-domain intervention`。

## 为什么跳过 R3

R3 的核心想法是把 PANDA 的 prototype similarity 推进为 supervised source utility routing。但 seed42 gate 证明当前 MVP 没有真正进入 non-self source utility：

- 所有正向 R3 variants 的 val F1/Acc 都未超过 deterministic strong control。
- `r3_effective_source_num_mean≈1.000006`。
- `r3_self_top1_ratio=1.0`。
- harmful / beneficial non-self alpha 约 `1e-7`。
- `corr(alpha, -regret)` 近 0。

因此失败不是“再加一点 reliability 特征就能救”的问题，而是机制层面被 self route 锁死。继续在 R3 v0 上堆参数会浪费算力，也容易写成审稿人一眼能打穿的 story。

R4 的设计目标是绕开这个失败模式：

| 旧问题 | R4 处理方式 |
| --- | --- |
| self domain 在 softmax 中压倒所有 source | non-self views 显式 mask self，不学习 self-vs-source router |
| alpha 近零导致外部 source 没有梯度 | 每个选中的 non-self view 都直接接 CE / KL / worst-view loss |
| 改 neighbor set 不改变 final boundary | 损失直接作用于 final logits |
| reliability selector 容易退化成 uncertainty control | MVP 先不依赖 reliability，reliability 只做二阶段权重消融 |
| test 结果诱导方法设计 | 只用 train/val gate，test 只确认 |
| R4 可能只是多 forward / augmentation | 先做 frozen-view validity gate，并加入 duplicate-anchor、self、random、bottom2、shuffled controls |

## 核心研究命题

PANDA 问的是：

```text
Which neighbor domain should be selected?
```

R4 改问：

```text
If the same sample is forced through plausible non-self source domains,
does the classifier remain correct and stable?
```

这比继续做 selector 更符合当前证据。因为我们已经知道：

- uncertainty / reliability 能解释错误；
- Gumbel selector 有 prediction-level 方差；
- 但仅改变 selector/ranking 不稳定，且常常不改变最终标签；
- R3 soft router 会塌缩到 self domain。

所以 R4 不把“选择邻居”作为第一目标，而把外部邻域当作模型内部的 source-domain intervention view，用训练损失直接塑造 classifier boundary。它不是严格因果反事实方法。

## 训练前生死门：Frozen-view Validity Gate

在任何 R4 训练前，必须先用 reproduced deterministic PANDA checkpoint 做只读 forced-view 诊断。目的不是证明 R4 有效，而是先证明 forced non-self source view 是有意义的模型内部干预；否则 R4 训练很可能只是普通一致性正则。

### 诊断对象

只用 train/val 做 gate；test 不导出、不打开、不解析。每个样本导出：

- deterministic anchor score。
- self-view score。
- PAD top2 non-self view scores。
- PAD bottom2 non-self view scores。
- shuffled PAD top2 view scores。
- random non-self view scores，至少 3 个 random source seeds。
- anchor-view JSD。
- score std。
- view flip rate。
- view correct rate。
- per-domain view CE。
- per-uncertainty-bin view CE。

### 通过线

训练前 validity gate 必须同时满足：

1. PAD top2 non-self view 与 anchor 有非零扰动：anchor-view JSD 或 score std 不能接近浮点噪声。
2. PAD top2 non-self 的 view CE / flip rate / JSD 至少不劣于 random non-self 和 bottom2 non-self。
3. self-view 明显不同于 non-self view；否则 forced-view 实现可能没有真正干预 source domain。
4. 若 PAD top2 与 random / bottom2 没有差异，后续论文不能声称 PANDA neighbor-domain knowledge 被利用，只能写普通 non-self intervention augmentation。
5. 若 forced views 几乎不改变 logits，当前 PAD-top2 forced-view D2 validity 不解锁 immediate training；本轮 R4 training smoke 为 `Not-Unlocked / No-Go only for current forced-view immediate-training permission`，不开 5-epoch gate。

该 gate 通过后，才允许进入 R4 seed42 训练 gate。

实际结果记录：

- 只使用 Weibo-21 seed42 train/val；test 未导出、未打开、未分析。
- Anchor direct verification max abs diff：train `0.0`，val `0.0`。
- Train split：PAD top2 CE `0.0002581242`，bottom2 CE `0.0002466201`，random mean CE `0.0002470063`，preliminary pass `False`。
- Val split：PAD top2 CE `0.1577833134`，bottom2 CE `0.1581670837`，random mean CE `0.1586489953`，preliminary pass `True`。
- Shuffled PAD top2 val CE `0.1568494840`，低于 PAD top2 CE `0.1577833134`，打穿 PAD ranking 主张。
- PAD top2 perturbation 非零但很小：train JSD `2.565e-07`，val JSD `1.424e-05`。
- 结论：R4 不进入 seed42 training gate；现仅作为 failed/weak intervention diagnostic 记录。

## 方法模块

### A. Non-self Source-domain Intervention View Generator

对每个训练样本，保留一个原始 deterministic PANDA anchor prediction，同时构造 `K` 个 non-self source-domain views：

```text
V_i = {s | s != domain_i, s in top-k PAD non-self domains or sampled non-self domains}
```

第一版建议：

```text
K = 2
view_source = pad_top2_nonself
self domain = masked
random non-self = control / robustness ablation
```

每个 view 通过强制 source-domain prompt / neighbor prompt 干预得到 view logits：

```text
z_i^0 = anchor deterministic PANDA logits
z_i^s = logits under forced non-self source s
```

关键点：

- self 不参与 view 集合，避免 R3 self-route collapse。
- view 不是学习到的 alpha 混合，而是显式 source intervention。
- 每个 view 都被 loss 直接监督，因此不会出现 non-self source alpha 近零导致无梯度。

### B. Counterfactual Supervised View Loss

每个 non-self view 仍应预测原样本标签：

```text
L_view = mean_i mean_{s in V_i} CE(y_i, z_i^s)
```

这是 R4 的最小闭环。它直接问：

```text
外部源域干预后，模型是否还能正确分类？
```

若这个 loss 有效，说明模型学到的是跨 source-domain prompt 的稳定判别边界，而不是只学会选择 self。

### C. Anchor-view Consistency

用 anchor prediction 和 non-self view prediction 做一致性约束：

```text
L_cons = mean_i mean_{s in V_i} JS(stopgrad(p_i^0), p_i^s)
```

第一版建议 anchor detach，避免错误 view 反向污染 anchor；同时保留 `L_view`，防止 anchor 错误时一致性把错误传播给所有 views。

### D. Worst-view Robustness

如果某个 source view 让同一样本损失显著变高，它就是 counterfactual negative transfer view。R4 不需要学习 router，也可以直接抑制 worst view：

```text
L_worst = mean_i max_{s in V_i} CE(y_i, z_i^s)
```

若 max 太不稳定，可以改成 CVaR / top-q 平均：

```text
L_cvar = mean_i mean_topq_s CE(y_i, z_i^s)
```

这比 R3 的 `alpha * regret` 更不容易被 alpha 近零吃掉。

### E. Counterfactual Sensitivity Reduction

额外记录并可选正则 view 间预测方差：

```text
S_i = std_s(p_i^s[label=1])
L_var = mean_i S_i
```

这个模块只作为稳定性辅助，不作为第一版 MVP 的主贡献。若它改善 ECE / Brier / HCE，但不改善 F1/Acc，应写成 reliability enhancement，不能包装成主性能方法。

### F. Reliability-weighted Extension

只有当无 reliability 的 R4 MVP 过线后，才加入 reliability 权重：

```text
w_i = detach(confidence_uncertainty_i)
L_view_weighted = mean_i w_i * mean_s CE(y_i, z_i^s)
```

必须同时跑：

- no-weight。
- confidence-uncertainty weight。
- overconfidence weight。
- random weight。
- shuffled weight。

若 no-weight 已经有效，论文主线应写 counterfactual domain consistency；若只有 confidence-uncertainty 有效，才谨慎写 reliability-weighted extension。

## 总目标函数

第一版 MVP 的 primary config 只固定一个，不允许在 seed42 上从多个 loss/lambda 组合里挑冠军：

```text
L = L_anchor
  + lambda_view * L_view
  + lambda_cons * L_cons
```

预注册 primary config：

```text
K:             [2]
view_source:   pad_top2_nonself
lambda_view:   0.1
lambda_cons:   0.05
anchor_detach: true
warmup_epoch:  1
consistency_mask: train-label CE/confidence mask only, no val/test correctness
```

`L_worst` / CVaR 不进入第一版 primary config，只作为二阶段 robustness ablation。原因是 worst-view 容易被少数噪声 source view 放大，若一开始放入主候选，失败后难以判断是 view CE、consistency 还是 worst-view 造成。

暂不加入：

- learned router。
- learned alpha。
- group loss。
- evidential head。
- source-utility pretraining。
- reliability weighting。

原因：第一轮 gate 只验证 non-self source-domain intervention views 是否能直接改变 final classifier boundary。模块越多，失败后越难定位。

## 与 R3 的关系

R3 的主命题是：

```text
learn source utility routing
```

R4 的主命题是：

```text
train classifier under explicit non-self source interventions
```

二者可以共享部分代码基础，例如 candidate source logits、forced source view 和诊断字段；但论文叙事必须切开：

- R3 是 failed routing hypothesis。
- R4 是 non-self source-domain intervention consistency hypothesis。

R4 不能继续沿用 `Regret-Regularized Reliable Routing` 题目，也不能把 R3 的 route/regret 结果包装成 R4 的成功证据。正式写作中最多写 `counterfactual-style source-domain intervention`，不能写成因果反事实方法。

## 预注册 Gate 设计

R4 gate 分两层，不能跳步：

1. Frozen-view validity gate：不训练，只用 held checkpoint 在 train/val 上导出 forced-view 行为，确认 non-self source-domain view 真会改变模型内部预测。
2. Seed42 primary training gate：只有 validity 通过后才允许训练。第一轮只跑 Weibo-21 seed42 5-epoch，不扩 seeds，不扩 Weibo。

训练 gate 运行前必须生成并冻结 `r4_gate_config.yaml`，至少包含：

- primary variant。
- `K`。
- view source。
- `lambda_view`。
- `lambda_cons`。
- warmup 规则。
- consistency mask。
- metrics。
- Go/No-Go 通过线。

seed42 结果出来后只允许 Go / No-Go，不允许补 lambda、换 primary、加模块或按 val 结果重写 R4。三 seed val 过线前不导出、不打开、不分析 test。

### 必跑对照

| Variant | 目的 |
| --- | --- |
| `panda_gumbel_short5` | 原始随机 selector 短训对照 |
| `deterministic_eval_l0` | 当前最强稳定对照 |
| `deterministic_train_l0` | 排除只是训练时去随机化 |
| `old_winning_control` | 排除只是复现旧 uncertainty control |
| `duplicate_anchor_ce_control` | 同样多 forward / 同样 CE 权重但不换 source，排除只是额外监督或训练步数 |

### R4 primary 与消融

| Variant | 目的 |
| --- | --- |
| `r4_view_ce_cons_top2_nonself` | 预注册 primary candidate |
| `r4_view_ce_top2_nonself` | 去掉 consistency，验证 view CE 本身 |
| `r4_cons_only_top2_nonself` | 只开 consistency，验证是否只是平滑正则 |
| `r4_view_ce_bottom2_nonself` | PAD 最不相似 non-self，对照 PAD top2 是否有意义 |
| `r4_shuffled_pad_rank_view_ce_cons` | 打乱 PAD source ranking，排除 PAD 排序只是噪声增强 |
| `r4_random_nonself_view_ce_cons_seed1/2/3` | 至少 3 个随机 non-self seeds，排除随机外域增强同样有效 |
| `r4_self_view_control` | self view control，证明不是重复 self 增强 |
| `r4_view_ce_worst_top2_nonself` | 二阶段 robustness ablation，不参与 primary 选择 |
| `r4_view_ce_cons_worst_top2_nonself` | 二阶段 robustness ablation，不参与 primary 选择 |

Reliability-weighted variants 暂不进入 MVP 主判断。只有 no-weight primary 过线后，才允许追加 confidence-uncertainty / overconfidence / random / shuffled weight extension。

### 机制诊断字段

每个 R4 run 必须导出：

- `r4_view_sources`。
- `r4_nonself_coverage`。
- `r4_anchor_score`。
- `r4_view_scores`。
- `r4_view_pred_flip_rate`。
- `r4_view_correct_rate`。
- `r4_intervention_score_std`，历史脚本若沿用 `r4_counterfactual_score_std` 字段名，论文写作中统一解释为 intervention sensitivity。
- `r4_anchor_view_jsd_mean`。
- `r4_worst_view_ce`。
- `r4_view_loss_by_domain`。
- `r4_view_loss_by_uncertainty_bin`。
- `r4_duplicate_anchor_control_score`，若运行 duplicate-anchor control。
- `r4_view_source_type`，例如 top2、bottom2、random、self、shuffled。

注意：R4 不用 route alpha，因此不再报告 `self_top1_ratio` 作为核心机制指标；它应报告 non-self view 是否被真正覆盖、view loss 是否下降、intervention sensitivity 是否降低。

## Go / No-Go 标准

### 进入 seeds 2024/2026 复核的最低线

Weibo-21 seed42 val 必须同时满足：

1. Frozen-view validity gate 已通过。
2. Macro-F1 和 Acc 都不低于 `deterministic_eval_l0`。
3. 至少一个主指标提升 >= 0.3pp；若低于 0.3pp，只能算边缘，不进入 seed 复核，除非机制指标极强且 weak-domain F1 也改善。
4. Paired bootstrap 或 McNemar/sign test 不能显示明显负向。
5. `r4_intervention_score_std` 或 `anchor_view_jsd` 相对 deterministic forced-view 诊断下降至少 10%。
6. sensitivity/JSD 的下降不能由 duplicate-anchor、self-view、random-nonself、bottom2 或 shuffled controls 同样达到。
7. R4 primary 必须优于 `self_view_control`，否则只是重复 self 增强。
8. R4 primary 必须优于 random non-self 三个 seeds 的均值，且不能只赢单次 random。
9. 若 bottom2 / shuffled / random non-self 与 PAD top2 同样有效，论文不能强写 PAD source selection，只能写 non-self source-domain intervention regularization。
10. Weak-domain F1 只作为辅助机制证据，不作为单独硬通过项，因为弱域样本量可能不足。

### 进入两数据集正式主表的最低线

1. Weibo-21 seeds 42/2024/2026 三 seed val mean 不低于 deterministic，最好 >= +0.3pp。
2. 至少 2/3 seeds Macro-F1/Acc 正向。
3. 任一 seed 相对 deterministic 的 Macro-F1/Acc drop 不允许超过 0.3pp。
4. 机制指标三 seed 方向一致：intervention sensitivity/JSD 应稳定下降，且不是 controls 同样下降。
5. seed2024 不能重演 old winning control 反例；若 seed2024 失败，则当前 frozen primary config / current training implementation 记为 D5 stability No-Go，不外推到全新 non-self/source protocol。
6. Test 只做 confirmatory，不根据 test 回头改 `lambda_view`、`lambda_cons`、view source、primary config 或 reliability 权重。
7. 若 Weibo-21 三 seed 过线，再扩 Weibo；Weibo 目标可以是 overall 不退化 + reliability / stability 指标改善。

### 失败时的止损线

如果 frozen-view validity gate 没过：

- 不启动 R4 训练。
- 不复核 seeds 2024/2026。
- 将当前 PAD-top2 forced-view intervention variant 记录为 failed current D2 variant / weak intervention diagnostic；全新 self-suppressed non-self source mixture 需新登记。

如果 seed42 val 没过 deterministic：

- 不复核 seeds 2024/2026。
- 不扩 Weibo。
- 不写 R4 为方法贡献。
- 将当前 R4 PAD-top2 forced-view 记录为 failed source-domain intervention consistency variant。历史上 R4 No-Go 后切换到 Round 2 方法候选池；Round 2、Round 3、Round 4 first-principle、Round 5 Gate-0 与 R5-A 单项 smoke 均已完成且未产生 `Primary-Candidate`。diagnostic/report 只作为证据和 fallback；全新 non-self/source protocol 需新登记和 D-level 验证。

如果 seed42 过线但 seed2024 失败：

- 不启动正式主表。
- 只能写成 future work 或附录边界条件。

## 审稿风险与预先反驳

| 审稿攻击点 | 风险 | R4 预防措施 |
| --- | --- | --- |
| 这只是数据增强 | 创新弱 | 强调增强对象是 PANDA 的 source-domain prompt / neighbor-domain intervention，不是普通文本/图片增强；报告 intervention sensitivity，并加入 duplicate-anchor / self / random / bottom2 / shuffled controls |
| 强制所有 source view 同标签会抹平领域差异 | 可能过正则 | 只用 PAD top2 non-self + 小权重；加 worst-view 而不是所有 source 强行等价 |
| 提升来自额外 forward / 参数 | 不公平 | 参数不增加或只复用同一 final head；报告训练开销；加 self-view / random-view control |
| 一致性会传播错误 anchor | 影响性能 | anchor detach + view CE；consistency warmup 后开启，且只用 train-label CE/confidence mask，不用 val/test correctness |
| 又变成 uncertainty control | 主张混乱 | MVP no-weight；reliability-weighted 只作二阶段消融 |
| 单 seed 偶然 | 可信度不足 | seed42 只做 fail-fast；预注册 primary config；必须 seeds 2024/2026 复核后才扩 Weibo |

## 当前执行顺序

1. 文档冻结 R3 MVP 为 No-Go，不继续当前 R3 路线。
2. 远端读取活代码，找出最小 forced non-self source view 插入点。
3. 先实现 held-checkpoint forced-view export，不训练，完成 frozen-view validity gate。
4. 若 validity gate 未过，当前 PAD-top2 forced-view training smoke 为 `Not-Unlocked / No-Go only for current immediate-training permission`。
5. 若 validity gate 通过，生成并冻结 `r4_gate_config.yaml`。
6. 实现 `selector_mode=r4_intervention` 或独立训练开关，优先复用 deterministic PANDA anchor。
7. batch size 2 smoke：forward/backward finite、view sources 不含 self、view logits shape 正确、旧 non-R4 checkpoint 兼容。
8. Weibo-21 seed42 5-epoch primary gate，只看 val 决策。
9. 若 gate 过线，再跑 seeds 2024/2026；否则止损。

## 当前投稿定位

R4 过线前，投稿保底仍是：

```text
PANDA reproduced baseline + reliability/uncertainty diagnostics + selector stability / failed-method boundary analysis
```

R4 只有在 frozen-view validity、seed42 primary gate 和 seed-recheck 都过线后，才可升级为方法论文主线。

当前 R4 未过 frozen-view validity，不能升级为方法论文主线。
