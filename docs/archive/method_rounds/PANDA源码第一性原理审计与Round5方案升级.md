# PANDA 源码第一性原理审计与 Round 5 方案升级

日期：2026-05-26

状态说明（2026-05-27 更新）：本文档是 Round 5 源码审计与升级记录。Round 5 active Gate-0 已闭环，R5-A 当前 image projection smoke 已 No-Go；R5-Prime/R5-A+D/R5-S 与 reserve 候选属于 `Not-Unlocked / Not-Evaluated`，不能写成组合或方法族失败。当前最新源码审计和候选池已升级到 `PANDA源码第一性原理审计与Round6方案升级.md` 与 `round6_candidate_registry.md`。

## 审计边界

本轮按用户要求连接云算力服务器，只读审计远端活代码：

```text
/root/autodl-tmp/panda_repro/panda
branch: innovation/reliability-disagreement
```

执行纪律：

- 只读审计，未修改远端文件。
- 未运行训练。
- 未导出、未打开、未分析 test。
- 用户提供的临时 SSH 凭据未写入任何项目文件或脚本。

调度了三个子代理：

1. 模块第一性原理审计。
2. 训练动力学与 Gate-0 插入点审计。
3. 整体架构重组审计。

## PANDA 当前实际信息流

远端 `model/PANDA.py` 的主路径不是一个完整端到端 source-domain adaptation 系统，而更像：

```text
frozen BERT / frozen MAE / frozen CLIP
-> text/image/fusion branch experts
-> h_di = h_text + h_image + h_fusion
-> static domain prompt bank + free domain prototypes
-> PAD/Gumbel top-k source selection
-> DCA(prompt-to-prompt only)
-> final_classifier([h_di, h_collab])
```

关键事实：

- BERT、MAE、CLIP 都是 frozen。
- text/image/fusion 的 PLE-style expert/gate forward 均 hardcode 使用 index 0。
- `domain_num=9` 只用于 prompt/prototype；前半段专家不是 9-domain expert。
- `domain_modal_prompts` 是静态可学习 prompt bank，不是由样本生成的 prompt。
- DCA 只看 target/source prompts，不看 `h_di` 或图文样本内容。
- `h_collab` 更像 domain/source bias，不是样本条件迁移知识。
- final boundary 的主要信息仍在 `h_di`。

## 模块断点

### 1. PAD/GNS 不足以训练 source selection

`_calculate_pad()` 基于自由参数 `domain_prototypes` 计算原型间距离，`_gumbel_neighbor_selector()` 返回离散 top-k index，再 gather source prompt。当前没有 straight-through 或 soft weighting，final BCE 很难反向塑造 PAD 排序。

此外，同域 prototype 到自身距离天然接近 0，self source 相似度极大。R3 soft router 的历史 gate 已显示 self top1 ratio 为 1.0，effective source 接近 1。也就是说，source 路线从第一性原理上会被 self prior 压住。

### 2. DCA 是 late static bias

DCA 的 query/key/value 都是 prompt，完全不看样本内容。已有 R4/P0-B/P1-A gate 也显示：forced source views 对 logits 有扰动，但 PAD top2 不稳定优于 bottom/random/shuffled。

结论：继续强化 late DCA 或换 source ranking，大概率仍然只是扰动 logits，不能稳定改变 final decision boundary。

### 3. prototype encoder/reconstruction 有断梯度风险

`proto_encoder(h_di)` 只用于 nearest prototype argmin；随后 gather prototype，再由 decoder 重构 `h_di`。argmin/gather 的索引不可导，`proto_encoder` 基本不从 reconstruction loss 获得有效梯度；prototype 更像自由码本，不是可靠 domain distribution estimator。

### 4. aux branch 信号没有成为 final 边界变量

text/image/fusion aux heads 有独立 BCE，且历史诊断显示 branch/fusion uncertainty 与错误强相关。但主路径只是：

```text
h_di = h_text + h_image + h_fusion
final = classifier([h_di, h_collab])
```

aux logits/reliability 大多 detach 后用于 selector。它们能解释错误，却没有内生进入 final boundary。Round 3 证明 late fusion / offline residual 会被 ordinary combiner 打穿，因此下一步必须转为训练期 branch-to-final 重排。

### 5. 多个历史模块未参与 PANDA 主路径

以下模块在 PANDA forward 中基本未用或弱用：

- `final_experts`
- `final_share_expert`
- `final_gate_list`
- `final_attention`
- `fusion_gate_list`
- `transformers`
- `mlp_img`
- `mlp_text`
- task/domain index 1 expert path

这说明直接声称 PANDA 已有完整 domain expert 架构很危险。新方案必须避开“修一下未训练 9-domain gate”这类路线。

## 新的第一性原理判断

Gate-0 前，旧 Round 5 的 A+D 组合仍然值得作为假设验证；源码审计后需要升级为更严格的 Gate-0 条件：

```text
PANDA 失败主因不是缺少更聪明的 source selector，
而是 source/domain/reliability/aux 信号都被放在 final boundary 之外或太晚的位置。
```

因此新方案优先级应从“先做 selector/边界微扰”调整为：

1. 先验证 branch-to-final 训练动力学是否断裂。
2. 再验证 low-margin boundary 是否脆弱。
3. 若二者成立，做 branch-consistent boundary-stress。
4. 若要重建 PANDA source/domain 叙事，必须把 prompt/source interaction 前移到中期样本条件融合。

## 升级后的候选池（Gate-0 前假设）

说明：本节是源码审计后的预注册候选池，不是 Gate-0 后的执行许可。实际结果见文末“Gate-0 后口径修正”：R5-Prime、R5-A+D 和 R5-S 当前均未解锁。

### R5-Prime：Branch-to-Final Evidential Arbitration

优先级：Gate-0 前最高；Gate-0 后已由 G0-E No-Go 关闭。

第一性原理：

branch/fusion uncertainty 是现有最强诊断信号之一，但当前只用于 selector 或后处理，不能稳定进入 final boundary。应把 aux branch 从“辅助损失”升级为“final 决策证据通道”。

核心机制：

- 不再裸用 `h_di = h_text + h_image + h_fusion`。
- 引入 branch evidence gate：

```text
h_evidence = w_t h_text + w_i h_image + w_f h_fusion
w = gate(h_text, h_image, h_fusion, p_text, p_image, p_fusion, uncertainty, domain)
```

- final head 使用 `[h_evidence, h_collab, branch uncertainty summary]`。
- 只在 low-margin / high-disagreement 样本上允许强 arbitration，避免 correct->wrong 变多。

Gate-0：

- G0-A：final BCE vs text/image/fusion aux BCE gradient conflict。
- G0-E：冻结 train/val probe，验证 `[final_logit, p_text, p_image, p_fusion, uncertainty, domain]` 的轻量 arbitration 是否 wrong->correct > correct->wrong，并且 val Macro-F1/Acc 至少不低于 original。
- 若 frozen probe 被 weighted-average final+aux 或 Platt 打穿，则 `No-Go for current frozen branch-evidential arbitration probe`；训练期 branch-to-final evidential mechanism 仍需 D4 才能排除。

强对照：

- final-only Platt / temperature。
- weighted average final+aux logits。
- final+random features。
- branch logits shuffled。
- reliability-only residual。
- same-param MLP without uncertainty。

### R5-A+D：Boundary-Stressed Branch-Consistent PANDA

优先级：Gate-0 前高；Gate-0 后未解锁，因为 G0-D destructive 且 G0-E No-Go。

第一性原理：

若 branch-final 梯度冲突集中在 low-margin / weak-domain 样本，且 frozen representation 对低 margin 小扰动敏感，那么主问题就是 final boundary 附近的分支更新不一致。

核心机制：

- R5-A：只在冲突层或边界脆弱样本上做 branch-final consistency / partial detach / sparse update。
- R5-D：只对 `h_di/h_collab/h_final` 的 low-margin 区域做 representation stress。
- 推理期不新增 memory、kNN、aux late fusion 或 source selector。

Gate-0：

- G0-A：记录 gradient cosine、norm ratio、cos<0、cos<-0.1 by branch/domain/low-margin。
- G0-D：用 train/val-only frozen representation 做 small perturbation 或 forced source boundary swap，记录 logit delta、flip、CE delta、correct->wrong、wrong->correct。
- A/D 必须同向：冲突样本也应是 boundary-sensitive 样本。

强对照：

- generic PCGrad / CAGrad / aux weight sweep。
- generic VAT / SAM / FGM / PGD / focal / label smoothing。
- random perturbation same norm。
- high-confidence perturbation。
- same-forward-budget control。

### R5-S：Sample-Conditioned Prompt Fusion

优先级：中高，是重建 PANDA source/domain 主叙事的候选。

第一性原理：

若 source/domain prompt 有用，它不应只在 final 前以静态 `h_collab` 拼接，而应在分支表征形成阶段改变样本“看什么”和“信什么”。

核心机制：

- 将 `domain_modal_prompts` 从 late DCA 前移到 text/image/fusion expert 后、aux head 前。
- 用 sample query 读全域 prompt memory：

```text
prompt_response = CrossAttn(query=f(h_text,h_image,h_fusion), key/value=domain_prompts)
h_prompted = h_branch + adapter(prompt_response)
```

- PAD 只作为 prior，不能硬 top-k 决定全部 source。

Gate-0：

- prompt swap / random prompt / all-domain mean prompt 的 logit delta 必须显著大于当前 DCA 弱扰动。
- learned/sample-conditioned route 必须优于 shuffled/random source。
- seed42 5-epoch val Macro-F1/Acc 不低于 deterministic。

强对照：

- static late DCA 原版。
- all-domain mean prompt。
- shuffled prompt。
- random source prompt。
- same-param MLP adapter。
- no prompt interaction。

### R5-P：Differentiable Non-self Source Router + Real Prototype Estimator

优先级：中，需谨慎重开 source 路线。

第一性原理：

现有 PAD/GNS 最大问题是 self domination、hard top-k 不可导、prototype 自由参数不是真实域分布。若继续 source/domain 路线，必须同时修这三个根因。

核心机制：

- 显式 non-self normalization。
- soft source weights，final loss 可回传到 router。
- source-specific adapter 作用于 `h_di`，不是只改 `h_collab`。
- prototype 改为 EMA/VQ/OT/MMD domain distribution estimator，加入 commitment/diversity。

Gate-0：

- route effective source number > 1.5。
- non-self source utility AUC > 0.6。
- PAD/source top 优于 bottom/shuffled/random。
- seed42 val Macro-F1/Acc 不低于 deterministic。

强对照：

- random non-self router。
- PAD-only non-self。
- shuffled reliability。
- same-param frozen router。
- always-self route。
- original free-prototype PAD。

### R5-I：Domain-Invariant / Domain-Specific Conservative Transfer

优先级：低到中，工程和审稿成本高。

第一性原理：

把 label-causal invariant boundary 和 domain-specific residual 分开；source transfer 只允许作用于 residual，不直接覆盖主标签边界。

Gate-0：

- `z_inv` label probe 不降，domain probe 降。
- `z_spec` 可预测 domain，但单独 label 能力受限。
- route 有 self/source/abstain coverage，不塌缩。

强对照：

- GRL-only。
- domain label shuffle。
- random subspace removal。
- always-self route。
- always-top2 PAD route。

## 执行协议升级

第一阶段只做 Gate-0，不跑正式训练：

```text
G0-A: branch-final gradient conflict
G0-D: low-margin boundary sensitivity
G0-E: branch-to-final arbitration frozen probe
G0-S: sample-conditioned prompt / source interaction feasibility
```

### Gate-0 赛马状态机

Round 5 的第一阶段是一个封闭的可行性赛马，不是看到某个方向有希望就提前 all-in。当前活跃候选池固定为 `G0-A/G0-D/G0-E/G0-S`；R5-P/R5-I/G0-B/G0-C 只作为 reserve 候选，除非前四项给出明确启用理由，否则不得抢占第一阶段资源。

状态流转：

```text
Pending
-> Running-Gate0
-> No-Go | Feasible-A | Feasible-B
-> All-Gate0-Done
-> Deep-Validation
-> Primary-Candidate
```

硬纪律：

- 若某候选的核心功能逻辑在 Gate-0 已无法实现，按 D-level 落状态：`D0/D1` 为 `Evidence-only/Blocked`，`D2/D3` 只关闭当前 probe/offline/frozen 变体，`D4` 才关闭当前训练实现；随后停止该 claim_scope 并切换下一个候选。
- 若某候选 Gate-0 成立，只能标记 `Feasible-A/B`；在 `G0-A/G0-D/G0-E/G0-S` 全部完成前，不能封主线，不能复核 seeds，不能扩 Weibo。
- 所有活跃 Gate-0 候选完成后，才允许比较 `Feasible-A/B` 候选，选择一个或多个进入深入验证。
- `Primary-Candidate` 只能在全部候选赛完后的深入验证阶段产生；任何单个 Gate-0 或 seed42 smoke 不能越级成为 `Primary-Candidate`。
- reserve 候选如果被激活，必须先补自己的 Gate-0 与强对照；未补完前不能参与主线排序。

推荐顺序：

1. `G0-A + G0-D + G0-E`。若三者同向，先把 R5-Prime / R5-A+D 标为优先深入验证候选；仍需完成 G0-S 后才能启动深入验证。
2. 若 branch-to-final 证据弱，但 G0-S prompt interaction 的 frozen intervention 强，则把 R5-S 标为可行候选。
3. 若 prompt/source 仍被 random/shuffled 打穿，不再重开当前 static/PAD-ranked source 路线；sample-conditioned prompt fusion、soft/non-self differentiable source mixture 或 EMA prototype 需新 manifest + D2/D3，过线后再 D4。
4. R5-P 只有在 non-self soft router 的 Gate-0 明确成立时进入 seed42 smoke。
5. R5-I 作为二阶段或附录机制，不抢第一主线。

必须先加实验护栏：

- `main.py` 默认是 `clean_vib`，所有 PANDA 运行必须显式 `--model_name FTmodel`。
- 当前 `Trainer.train()` 最后默认跑 test；Round 5 方法选择前必须新增 `--skip_final_test` 或使用 val-only runner。
- `selector_mode=deterministic` 训练期仍会加 Gumbel；训练期确定性必须用 `deterministic_train`。
- `num_workers=0` 用于 Gate-0 和三 seed val，减少 worker seed 干扰。
- 指标统一用 `>=0.5` threshold 的工具脚本，避免 `np.around` 与工具结果混用。

## Gate-0 前最终建议

Gate-0 前，建议把 Round 5 主线从泛化的 “Training-Dynamics Rebuild” 收紧为：

```text
Branch-Evidential Boundary Rebuilding for PANDA
```

写作主张：

```text
PANDA 的 source-domain adaptation 失败并不是 source ranking 本身不足，
而是 branch evidence、domain prompts 和 source knowledge 都没有在训练期稳定内生进入 final decision boundary。
我们先用 gradient/boundary/probe 诊断定位断点，
再用 branch-evidential arbitration 与 boundary-stressed consistency 重建 final boundary。
```

这条线最贴合已有证据：

- branch/fusion uncertainty 是强诊断信号。
- 当前 D3 offline late aux residual 已 No-Go，所以若重开必须做训练期内生机制并新建 manifest。
- DCA/source views 是弱扰动，所以不能继续 late source reranking。
- PAD/GNS 不可导且 self dominated，所以 source 路线不能作为第一主线。

## Gate-0 后口径修正

2026-05-26 Round 5 `G0-A/G0-D/G0-E/G0-S` train/val-only Gate-0 已完成，深度复盘后需要把上述写作主张降调：

- `G0-A` 支持的是 image-branch/final gradient conflict 候选信号，而不是完整 branch-evidential boundary rebuilding 已成立。Image branch conflict rate 为 `0.337662`，但 low-margin/error enrichment 都很薄，且是 batch-level 统计。
- `G0-D` 支持的是 final boundary fragility 诊断，而不是 R5-D 训练方向。Boundary shrink 将 F1/Acc 从 `0.956086/0.956098` 拉低到 `0.939832/0.939837`，flip audit 为 `7 wrong->correct / 17 correct->wrong`。
- `G0-E` 已关闭 R5-Prime：branch evidential arbitration F1/Acc `0.933129/0.933333`，且 shuffled branch-logit control 略高，不能证明 branch evidence 有序可用。
- `G0-S` 已关闭 source/prompt 路线：PAD top2 CE `0.157783` 被 shuffled PAD top2 CE `0.156849` 打穿。

因此当前标题可继续作为诊断方向名，但不能写成已成功方法。Gate-0 后要求先做 R5-A 单项 seed42 smoke，并把贡献限定为 PANDA-specific image-branch/final gradient conflict handling；该约束已在 2026-05-26 执行，且因 primary 低于 deterministic、被 aux weight control 打穿而对当前 image projection 训练实现 No-Go。R5-Prime/R5-A+D/R5-S 未直接 D4 训练验证，只能写 `Not-Unlocked`。

## R5-A Smoke 后口径修正

2026-05-26 R5-A 单项 seed42 smoke 已完成，仍为 train/val-only；test 未导出、未打开、未分析。预注册 primary `r5a_image_project_l1p0` 只验证 image-branch/final gradient conflict candidate signal 是否能训练期闭环，不验证 source/domain/reliability/prompt 机制。

结果为 `No-Go for current r5a_image_project_l1p0 training implementation`：

- deterministic baseline val F1/Acc 为 `0.938175/0.938211`。
- primary `r5a_image_project_l1p0` 为 `0.936504/0.936585`，低于 deterministic。
- best control `aux_weight_2p0` 为 `0.939837/0.939837`，打穿 primary。
- primary image conflict rate 降到 `0.058442`，但 flip audit 为 `9 wrong->correct / 10 correct->wrong`，净负。
- `aux_weight_2p0` image conflict rate 更低，为 `0.024675`，flip audit `16/15` 净正。

解释边界：

- R5-A 的 image projection 不构成 `Primary-Candidate`，不复核 seeds 2024/2026，不扩 Weibo。
- `aux_weight_2p0` 说明 aux supervision 强度可能影响图像分支信号吸收，但它是 control，不是当前方法成功。
- `G0-B/G0-C` 仍按 superseded reserve 处理；除非新证据触发并补独立 Gate-0 与强对照，否则不启动。
- 任何后续写作只能说：G0-A/R5-A 揭示了“降低冲突 telemetry 不等于提升 final boundary”的失败边界。
