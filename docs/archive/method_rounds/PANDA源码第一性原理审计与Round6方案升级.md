# PANDA 源码第一性原理审计与 Round 6/7 方案升级

日期：2026-05-27

## 审计边界

本轮按用户要求重新连接云算力服务器，只读审计远端活代码：

```text
/root/autodl-tmp/panda_repro/panda
branch: innovation/reliability-disagreement
```

执行纪律：

- 已调度四个并行子代理，分别审计架构数据流、loss/aux/梯度生命周期、创新挂点和赛马实验协议。
- 主线同步审计远端 `main.py`、`run.py`、`model/PANDA.py`、`utils/`、`tools/` 和已有 gate 产物结构。
- 本轮只做静态代码阅读、接口级分析和协议设计。
- 未启动训练，未导出、未打开、未分析 test。
- 用户提供的 SSH 凭据未写入任何项目文件、脚本或文档。

## 一句话结论

PANDA 当前最硬的断点不是“还缺一个更聪明的 source selector”，而是：

```text
domain/source/reliability/branch 信号大多在 final boundary 之外、太晚或不可导的位置发挥作用；
branch aux supervision 有真实线索，但默认等权 aux BCE 没有被组织成稳定的 final-boundary shaping 机制；
现有代码还混有大量未进入 forward 的历史模块，使 domain expert、prompt 和 selector 叙事容易被误读。
```

因此，下一轮不能继续沿 PAD/source reranking、late DCA、offline aux-logit residual 或 R5-A image projection 调参。必须把候选池重新定义为“先证明核心机制能不能进入 final boundary，再训练”。

## 远程源码确认的实际数据流

重要前置：`main.py` 默认 `--model_name clean_vib`，并不会跑 PANDA。只有显式设置 `--model_name FTmodel`，`run.py` 才会实例化 `model.PANDA.Trainer`。后续所有 PANDA smoke / gate 必须把这个作为 Gate-0 前置检查。

```text
Excel/CSV/Pkl
 -> utils/*_clip_prompt.py::load_data
 -> TensorDataset:
    token_ids, masks, label, category, image, clip_image, clip_text,
    input_ids, attention_mask, text_loss_ids
 -> utils.utils::clipdata2gpu
    只保留前 7 个字段，丢弃 prompt input_ids/attention_mask/text_loss_ids
 -> model/PANDA.py::MultiDomainPLEFENDModel.forward
    frozen BERT(content) -> text tokens
    frozen MAE(image) -> image tokens
    frozen CN-CLIP(image,text) -> clip fusion
    text/image/fusion experts + gates(index 0 only)
    -> h_text, h_image, h_fusion
    -> aux heads: p_text, p_image, p_fusion
    -> h_di = h_text + h_image + h_fusion
    -> free domain prototypes / PAD / top-S selector
    -> static domain_modal_prompts / DCA
    -> h_collab
    -> final_classifier_panda([h_di, h_collab])
    -> y_score
 -> Trainer.test
 -> metricsTrueFalse / metrics
```

关键文件：

| 位置 | 作用 | 审计结论 |
| --- | --- | --- |
| `main.py:5-85` | CLI 与配置入口 | 默认不是 PANDA；PANDA 实验必须显式 `--model_name FTmodel` |
| `run.py:117-196` | dataloader 与 trainer 接线 | `FTmodel` 才进入 `model.PANDA.Trainer` |
| `utils/weibo21_clip_prompt.py:155-190` | Weibo-21 TensorDataset 构造 | 生成 prompt 字段，但后续 PANDA 未消费 |
| `utils/utils.py:39-49` | `clipdata2gpu` | 只传前 7 个字段，prompt 输入被丢弃 |
| `model/PANDA.py:104-848` | PANDA 主模型 | branch/PAD/DCA/final 都在同一大类里，模块边界不清 |
| `model/PANDA.py:329-352` | PAD 计算 | 基于自由 domain prototypes，不是样本条件 source utility |
| `model/PANDA.py:524-590` | neighbor selector | hard top-k index，注释称 Gumbel 可微，但 final loss 不会连续塑造 PAD 排序 |
| `model/PANDA.py:1191-1307` | train/checkpoint/test | checkpoint 按 val final metric 保存；常规 test 不记录 branch 指标 |
| `tools/evaluate_panda_selector_variants.py` | held-checkpoint 评估 | 已能导出 final、branch、selector、ECE/Brier 等赛马指标 |

## 模块级第一性原理审计

### 1. domain expert 叙事不能直接成立

代码里 `domain_num=9` 只用于 prompt/prototype/PAD；text/image/fusion gate 和 expert 是 `task_num=2` 组，forward 里硬编码使用 index 0。`category` 没有进入前半段 expert routing。

结论：

- 不能把现有 expert/gate 写成 9-domain expert。
- 不能把 task index 1 当 domain route 证据。
- 若未来重开 domain-conditioned expert，必须新增明确的 9-domain 或 sample-conditioned adapter，并用 random-route / domain-shuffle / parameter-matched controls。

### 2. prompt 路径存在但未被 PANDA 消费

dataloader 构造了 OpenPrompt 相关 `input_ids/attention_mask/text_loss_ids`，但 `clipdata2gpu` 丢弃它们，PANDA forward 实际只用普通 BERT token。

结论：

- 当前 DMPG/prompt 叙事主要来自静态 `domain_modal_prompts`，不是文本 prompt mask 表征。
- 若要做 prompt 创新，必须先做接口可行性检查：prompt 字段是否进入 model、shape 是否一致、旧 checkpoint 是否兼容。

### 3. PAD/GNS 与样本特征弱耦合且梯度路径不硬

PAD 只由全局自由参数 `domain_prototypes` 算出 domain-to-domain 距离；样本只提供 target domain id。随后通过 top-k index gather source prompts，缺少 soft/straight-through routing。

结论：

- 继续调 PAD/source ranking 很可能仍被 random/shuffled/bottom controls 打穿。
- 若重开 source 路线，必须同时解决三点：non-self self-prior、soft可导 source mixture、source representation 进入 `h_di` 或 final boundary，而不是只改 late `h_collab`。

### 4. DCA 是 late static domain bias，不是样本条件知识迁移

DCA 的 query/key/value 都来自 `domain_modal_prompts`，不看当前样本的 `h_di`、branch conflict 或图文内容。已有 R4/P0-B/P1-A 也显示：source/prompt view 会弱扰动 logits，但 PAD top2 不能稳定打过 shuffled/random/bottom controls。

结论：

- late DCA/source prompt 不宜作为下一轮主线。
- 如果想保留 PANDA source/domain 叙事，必须把 prompt interaction 前移到 branch feature 形成阶段，并做 sample-conditioned soft memory，而不是再调 top-k。

### 5. aux branch 是最值得保留的新线索，但不能沿 R5-A 叙事

训练 loss 当前为：

```text
BCE(final) + lambda_rec * loss_rec
+ aux_loss_weight * mean(BCE(text), BCE(image), BCE(fusion))
```

aux heads 能输出 `p_text/p_image/p_fusion`，已有诊断说明 branch/fusion uncertainty 能解释错误；R5-A smoke 又显示 `aux_weight_2p0` 比 image projection primary 更强。但这只是新的 candidate signal，不是 R5-A 成功。

结论：

- `aux_weight_2p0` 只能作为 R6-A 的起点。
- R6-A 必须验证 aux supervision 的强度、分支配比、时序和 final alignment，而不是只复述“加大 aux weight 有用”。
- 如果最佳结果只是静态 aux weight sweep，论文主张只能降级为 auxiliary-supervision sensitivity，不能包装成复杂机制。

补充 loss/梯度生命周期审计：

- 配置从 `main.py --aux_loss_weight/--r5a_grad_mode` 进入 `run.py`，最终在 `model/PANDA.py::Trainer.train` 中组装 loss。
- 当前 R5-A smoke 中 `selection_margin/regret/route_balance` 均未打开，实际比较的是 final BCE、reconstruction 和 aux BCE 的训练动力学。
- `r5a_grad_mode=image_project` 只处理 image branch 的梯度几何；text/fusion 仍走普通反传。generic PCGrad/CAGrad 是强对照，不是 PANDA-specific 方法本身。
- checkpoint 只保存 `state_dict`，由验证集 `metric` 即 Macro-F1 触发；不保存 optimizer/scheduler 状态。因此 smoke 的 checkpoint 生命周期必须额外记录 epoch-to-best、日志路径和可复现命令。
- 前向返回 sigmoid 概率，训练使用 `BCELoss`；aux 增强可能先改变置信度、ECE/Brier/HCE 和 branch conflict telemetry，不必然改变 0.5 阈值处的 final decision boundary。
- R5-A 证据必须降调：`aux_weight_2p0` val F1/Acc/ECE 为 `0.939837/0.939837/0.011093`，强于 deterministic 的 `0.938175/0.938211/0.032676` 和 image_project primary；但这只是 control anchor，不是 R5-A 胜利。

### 6. 常规 eval 不够完整

`Trainer.test()` 只返回 final prediction 的指标；branch 指标、branch-final gap、selector margin、correct->wrong 等需要诊断工具导出。`panda_gumbel` eval 还可能带邻域随机性，协议比较应优先用 `deterministic_train` 或明确重复评估。

结论：

- 任何新 gate 都必须配套诊断导出，不只看 stdout 的 `Final`。
- Gate-0 指标必须包括 final、branch、flip audit、strong controls 和训练成本。

## 新候选池：按第一性原理重新排序

### R6-A：Auxiliary-Supervision Rebalancing for Branch-to-Final Alignment

优先级：P0，当前最值得先冻结协议的候选。

核心假设：

```text
PANDA 的 branch features 已经被 aux heads 直接监督，
但默认 mean(aux BCE) 的强度、分支配比和训练时序没有被校准到 final boundary。
通过可解释的 aux rebalancing，让 branch supervision 在训练期塑造 h_di，
可能比 R5-A image projection 更直接。
```

最小实现候选：

- static aux sweep：`0.0/0.5/1.0/1.5/2.0/3.0`。
- warm strong branch shaping：前期 aux `2.0`，后期回到 `1.0`。
- late branch sharpening：前期 aux `0.5`，后期升到 `2.0`。
- branch-specific aux：image/text/fusion 分支不同权重。
- final-aligned aux：只在 branch 与 final 同向、或 low-margin 区间增强 aux。
- detached aux control：aux loss 只计数值或只更新 aux head，不更新 branch feature。
- final-branch consistency：对 final 概率和 branch 均值或 branch logits 加 KL/JS/margin alignment，只能作为 R6-A 子候选，必须打过静态 aux sweep。
- image+fusion gradient projection：从 R5-A image-only 扩展到 fusion/shared trunk 的可行性子候选；由于 R5-A image_project 已 No-Go，该线默认作为强对照/二级候选。

Gate-0 可行性：

- 先不训练：复用已有 frozen/common 导出与 R5A telemetry，确认 branch-final conflict、branch evidence 与 low-margin/error 的关系。
- 必须先确认 `aux_weight_2p0` 是 control anchor：任何 primary 若不能超过它，只能降级为 sensitivity/control 结果。
- 冻结 manifest 后才能做 seed42 5-epoch train/val-only smoke。

No-Go：

- primary 低于 deterministic。
- primary 输给 best static aux sweep。
- primary 输给 `aux_weight_2p0` control anchor。
- 只改善 ECE/Brier/HCE 或 conflict telemetry，不改善 final F1/Acc。
- `correct_to_wrong >= wrong_to_correct`。
- random/shuffled aux、same-budget、final-only longer epoch 同样有效。

### R6-B：Evidence-Gated Branch Aggregation

优先级：P0/P1，是最接近 final boundary 的结构候选之一。

核心假设：

```text
h_di = h_text + h_image + h_fusion 的裸相加太粗；
应该按 branch confidence、entropy、disagreement 和 sample uncertainty
决定 text/image/fusion 哪条 evidence 更可信。
```

最小实现：

- 先做 frozen train/val offline gate：用 `p_text/p_image/p_fusion`、branch entropy、branch disagreement、final margin 学一个极小 branch weight。
- 训练实现若解锁，只在 `h_di` 生成处替换等权相加：

```text
h_evidence = w_t h_text + w_i h_image + w_f h_fusion
```

Gate-0：

- 对比 equal-sum original、scalar weight、logistic stacking、final+aux weighted average、shuffled-confidence、random-confidence。
- 必须证明收益不是 Platt/temperature 或普通 final+aux stacking。

No-Go：

- 只改善 calibration，不改善 final F1/Acc。
- shuffled-confidence/random-confidence 或 ordinary stacking 追平。
- low-margin / high-disagreement 样本没有局部收益。

### R6-C：Boundary-Local Lightweight Calibration, Diagnostic Only Unless Flip Net Positive

优先级：P0/P1，但默认降调。

核心假设：

```text
PANDA 的 final boundary 已很强，低 margin 样本局部脆弱；
如果只做极小 boundary adapter，可能比改 DCA/source 更直接。
```

这条来自 G0-D 的 Feasible-B 信号，但 G0-D 已暴露 destructive risk。因此它不是优先训练主线，只能作为局部边界上限诊断。

Gate-0：

- frozen `h_di/h_collab/h_final` 上做 final-only logit calibration、low-margin tiny adapter、mask-vs-random mask。
- 必须报告 low-margin bin、weak-domain、high-confidence-correct flip。

No-Go：

- correct->wrong 超过 wrong->correct。
- Platt/temperature/logit bias 控制同样有效。
- val Macro-F1/Acc 低于 original。

### R6-D：Cross-Architecture Disagreement Distillation

优先级：P1，和 PANDA 内部结构本质不同。

核心假设：

```text
PANDA 内部 source/domain/branch 信号多次被 controls 打穿；
如果 MMDFND/DAMMFND 与 PANDA 的错误互补真实存在，
跨架构 teacher 可能提供比 PANDA 自身 aux/reliability 更干净的监督信号。
```

Gate-0：

- 只做 train/val offline complementarity。
- 计算 teacher-correct/PANDA-wrong 覆盖率、oracle upper bound、soft logit complementarity。
- 不训练、不打开 test。

No-Go：

- 互补不超过 self-distill/random teacher。
- 增益只来自 temperature/calibration。
- teacher 需要 test 选择。

### R6-E：Deep Supervision + Early-Exit Diagnostic

优先级：P1。

核心假设：

```text
aux heads 本身就是 early-exit 入口；
容易样本也许不需要 late DCA/final head，
但该机制只有在 low-margin/high-disagreement 样本不受损时才有方法价值。
```

Gate-0：

- frozen train/val 先比较 always-final、always-exit、confidence-gated exit、random-exit、shuffled-confidence exit。
- 记录 coverage-risk、low-margin 子集、wrong->correct/correct->wrong。

No-Go：

- 只筛出 easy 样本，不能提升 full-coverage final。
- coverage 降太多或阈值选择需要 test。
- random/shuffled-confidence exit 同样有效。

### R6-F：Label-Preserving Modality Robustness

优先级：P1。

核心假设：

```text
h_di = h_text + h_image + h_fusion 的裸相加可能让单模态错误支配 final；
但跨样本图文替换风险太高，所以只允许同样本 label-preserving view consistency。
```

Gate-0：

- frozen view delta：text-drop、image-drop、fusion-drop 是否真实扰动 logits。
- 训练前先验证 full-view vs dropped-view 的 branch reliance 和 final flip 分布。

No-Go：

- 普通 dropout/R-Drop/label smoothing 同样有效。
- full-view 主指标下降。
- consistency 抹掉真假新闻有效冲突 cue。

### R6-G：Soft Prototype Memory / EMA Prototype Estimator

优先级：P2。

当前状态：`No-Go for current direct D2/D3 frozen soft/EMA prototype probe`。2026-05-27/28 已补 hard-vs-soft-vs-EMA/prototype sensitivity direct probe；best primary 与 original 持平，且 random/shuffled controls 可匹配或更强。该结论只覆盖当前 frozen probe，不永久排除训练期 prototype memory。

核心假设：

```text
当前 torch.min + gather 的 hard prototype 路径近似断梯度；
domain_prototypes 更像自由码本，而不是真实域分布估计器。
```

Direct Gate-0：

- 不训练先做 prototype sensitivity：hard nearest、soft assignment、EMA/frozen train prototype、random prototype、class-shuffled memory。
- 观察 source ranking、h_collab、final logits 和 CE 是否出现强于 random/shuffled 的边界。

No-Go：

- soft prototype 只是平滑，不改变 source ranking 或 final boundary。
- random/class-shuffled prototype 同样有效。
- 参数/记忆规模上升但主指标无收益。

### R6-H：Sample-Conditioned Prompt Memory

优先级：P2，只有 source/domain 叙事必须保留时才重开。

核心假设：

```text
如果 domain prompt 有用，它应该被当前样本 query 读取，
并在 branch feature 形成阶段影响 h_text/h_image/h_fusion，
而不是在 final 前 late concat 一个 static h_collab。
```

Gate-0：

- 不训练先做接口 smoke：prompt field 是否可进入 PANDA、sample query cross-attn shape 是否一致。
- frozen forced prompt response 必须显著强于 late DCA 的弱扰动，并打过 shuffled/random prompt。

No-Go：

- prompt response 仍只产生微小 logit 扰动。
- random/shuffled prompt 同样有效。
- 同参数 MLP adapter 更强。

### R6-I：Domain-Conditioned Final MoE / Low-Rank Boundary Adapter

优先级：P2。

核心假设：

```text
现有 branch expert 不是 domain expert；
如果需要 domain conditioning，应在 final boundary 上新增明确、极小、可控的 domain-conditioned adapter，
并打过 random-domain 和 same-param controls。
```

Gate-0：

- frozen/offline 比较 fixed final head、domain-conditioned residual、random-domain labels、same-param MLP、domain-bias-only。
- 若借鉴 MMDFND-style domain embedding + gate，必须限制参数并报告 expert collapse。

No-Go：

- random-domain route 或 same-param MLP 追平。
- domain expert 塌缩到单一路径。
- domain conditioning 带来 leakage 风险但 final 指标不升。

### R6-J：Differentiable Non-self Source Mixture

优先级：P2/P3，谨慎保留。

当前状态：`No-Go for current direct D2/D3 frozen self-suppressed non-self mixture probe`。2026-05-27/28 已补全新 self-suppressed non-self source-mixture direct probe；PAD soft non-self variants 与 original 持平，且 random/shuffled controls 可匹配或更强。该结论只覆盖当前 frozen probe，不永久排除训练期 source-mixture 新实现。

核心假设：

```text
现有 PAD/GNS 的根因是 self domination、hard top-k 和 free prototypes；
如果继续 source 路线，必须改成 non-self soft mixture，并让 final loss 可回传到 source utility。
```

Direct Gate-0：

- effective source number > 1.5。
- non-self alpha 与负 regret 相关。
- source top/bottom/random/shuffled controls 有清晰边界。

No-Go：

- self route collapse。
- random/shuffled source control 打穿。
- final 指标低于 deterministic。

## 赛马式研发协议

### 状态机

```text
Candidate-Registered
-> Gate0-Frozen
-> Gate0-Running
-> Blocked / No-Go / Feasible-B / Feasible-A
-> All-Candidates-Gated
-> Smoke-Frozen
-> Smoke-Running
-> Smoke-No-Go / Smoke-Feasible
-> Deep-Validation
-> Primary-Candidate
-> Three-Seed-Val
-> Confirmatory-Test
```

### 候选登记表字段

每个候选必须先登记：

```text
candidate_id
family
hypothesis
code_path
minimal_change
expected_signal
primary_baseline
strong_controls
gate0_inputs
forbidden_inputs
metrics
go_rule
no_go_rule
checkpoint_lifecycle
promotion_rule
```

### Gate-0 共用规则

- Gate-0 优先使用 frozen checkpoint、train/val common export、已有 telemetry 和接口 shape 检查。
- Gate-0 阶段不训练。
- 任何路径需要 test 才能成立，直接 `No-Go`。
- 代码路径不存在、旧 checkpoint 不兼容或关键张量不可导出，标记 `Blocked`，不靠猜测进入训练。
- 候选失败立即切换下一个候选。
- 候选可行只标记 `Feasible-A/B`，继续验证其他候选。

### Smoke 共用规则

当前规则更新：R6-A 已在单独 `round6_r6a_smoke_manifest.json` 的 `FROZEN_SMOKE` 约束下完成 seed42 5-epoch train/val-only D4 smoke，并判定当前训练实现 `No-Go`。未来如果重新提出 R6-A 或本质不同的新候选，必须重新建 manifest 并写明 train/val-only、强对照、checkpoint lifecycle 与 No-Go 线；不得复用当前 No-Go smoke 作为继续训练许可。smoke 的基础配置如下：

```text
dataset=weibo21
seed=42
model_name=FTmodel
selector_mode=deterministic_train
batchsize=32
lr=1e-4
epoch=5
early_stop=6
num_workers=0
skip_final_test=true
```

必须记录：

- final：Macro-F1、Acc、AUC、ECE、NLL/log-loss、Brier、HCE。
- branch：text/image/fusion Acc、Macro-F1、AUC、ECE、NLL、branch-final gap。
- flip audit：wrong->correct、correct->wrong、high_conf_correct_to_wrong、changed_count。
- bins：low margin、weak-domain、high-disagreement、high-confidence-correct。
- controls：best primary、best static/control/random/shuffled、primary-control margin。
- cost：wall time、GPU、peak memory、epoch-to-best、checkpoint path、log path。

### 强对照底线

每个候选必须至少打过：

- deterministic eval / deterministic train。
- same-budget noop。
- final-only calibration：temperature / Platt / logit bias。
- final+aux ordinary stacking 或 weighted average。
- random feature / shuffled feature。
- label-shuffled / source-shuffled / prompt-shuffled control。
- parameter-matched adapter control。

R6-A 额外必须打过：

- static aux sweep。
- random aux labels。
- shuffled branch-label mapping。
- detached aux/no-feature-update control。
- generic PCGrad/CAGrad/GradNorm/DWA 至少两个。
- final-only longer-epoch control。

### 晋级规则

- `Feasible-A`：primary final F1/Acc 不低于 deterministic，理想要求 `>= +0.3pp`；强对照全部落后；flip audit 净正；至少两项支持指标不劣化。
- `Feasible-B`：核心机制存在，但增益弱、论文张力不足或有 correct->wrong 风险；可保留为二阶段/附录/诊断，不抢主线。
- `No-Go`：低于 baseline、被 control 打穿、只改善 calibration、flip audit 净负、需要 test 选择、或不可复现。
- 全部候选 Gate-0 完成前，不允许把任何单个可行候选封为主线。
- 所有 smoke 完成后，只对存活候选做三 seed val 复核。
- test 只在三 seed val 固定 primary config 后做 confirmatory。

## 当前冻结与闭环状态

已完成：

1. 子代理 loss/aux 梯度生命周期和跨领域创新挂点审计已回收，并并入本文件、`round6_candidate_registry.md` 和 `round6_r6a_gate0_manifest_TEMPLATE.json`。
2. Round 6 初版文档已更新状态说明，云端源码事实以本文件和候选登记表为准。
3. 已生成 `round6_candidate_registry.md`。
4. 已生成 `round6_r6a_gate0_manifest_TEMPLATE.json`，状态为 `DRAFT_NOT_FROZEN`，`training_allowed=false`；该文件现在仅保留为历史草案模板。
5. 2026-05-27 第二轮蓝军反审已完成并关闭 4 个子代理：源码挂点、协议口径、runner 可执行性、审稿风险均确认 R6-A 不能直接 smoke。
6. 已新增正式 `round6_r6a_gate0_manifest.json`，状态为 `FROZEN_GATE0_NONTRAINING`，只冻结非训练 Gate-0 协议；`training_allowed=false`、`smoke_training_allowed=false`。
7. 已完成 R6-A implementation gap patch：远端 `main.py/run.py/model/PANDA.py` 支持 branch-specific aux 权重、aux schedule、detached/no-feature-update aux、random/shuffled aux label controls，并通过非训练 `py_compile`、argparse、静态透传、Trainer signature 和 helper semantic sanity；未启动训练，未导出/打开/分析 test。
8. 已新增 R6-A dry-run runner/summarizer：`tools/run_panda_round6_r6a_smoke.sh` 和 `tools/summarize_panda_round6_r6a_smoke.py`。runner 默认拒训，只有 `--dry-run` 打印命令；真实训练还需 `--allow-training`、`ALLOW_R6A_TRAINING=1` 和 `FROZEN_SMOKE` manifest。summarizer 支持 empty-summary，缺 metrics 时输出 `Blocked` 且 `training_allowed=false`。
9. 已新增并冻结 `round6_r6a_smoke_manifest.json`，状态 `FROZEN_SMOKE`，仅授权 Weibo-21 seed42 train/val-only D4 smoke；R6-A 19 个 variants 已完成并落盘到 `remote_panda_work/repro_logs/round6_r6a_smoke/seed42/`。
10. R6-C seeds 2024/2026 offline replication、R6-D cross-architecture complementarity、R6-G direct soft/EMA prototype、R6-H frozen prompt-response、R6-J direct self-suppressed source-mixture probe 已补齐。

当前 Round 6/7 闭环：

1. R6-A 已完成 D4 seed42 smoke 并判定 `No-Go`：best primary `r6a_late_aux_ramp_0p5_to_2p0` F1/Acc `0.938184/0.938211`，低于 best control `static_aux_weight_2p0_anchor_control` 的 `0.939837/0.939837`；flip `13/12` 也不优于 control `17/15`。
2. R6-C seed42 弱正信号在三 seed offline replication 中不稳定：seed2024 为负，seed2026 被 calibration/global control 打穿，只保留 low-margin diagnostic。
3. R6-D/R6-G/R6-H/R6-J 的误杀风险补实验已完成，当前 direct/complementarity/frozen-response 变体均 `No-Go`；R6-B/R6-E/R6-F/R6-I 当前 frozen/offline 变体也已 `No-Go`。
4. 当前没有 `Primary-Candidate`，不复核 seeds、不扩 Weibo、不导出/打开/分析 test。下一步必须复盘是否提出本质不同的新候选，或收口为诊断/失败边界论文材料。

## Round 7 重新开池

2026-05-28 已新增 Round 7 规划入口：

- `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md`
- `round7_candidate_registry.md`
- `round7_gate0_manifest_TEMPLATE.json`

Round 7 的主命题不是继续改 source、prompt、prototype、offline adapter 或 inference selector，而是：

```text
把 reliability、branch conflict、low margin、weak-domain 等风险信号
在训练期内生写进 final decision boundary。
```

候选池：

1. `R7-A Boundary-Risk Aware Training`
2. `R7-B Branch-to-Final Disagreement Distillation`
3. `R7-C Error-Region Contrastive Boundary Learning`
4. `R7-D Confidence-Calibrated Auxiliary Curriculum`

执行口径：

- Round 7 当前为 `D0 Planning / Pending / Not-Evaluated`，不继承 Round 6 的 No-Go。
- R6 的所有负结果只作为强对照和风险先验：static aux 2.0、ordinary stacking / KD、random/shuffled risk、random/shuffled branch teacher、random/class-prior memory、same-budget longer training 等。
- 四个候选必须先完成 train/val-only artifact audit 与 D2/D3 核心机制实验；缺 artifact 时补 export 或标 `Blocked`。
- 任何 R7 训练期方法至少到 `D4 Seed42-Smoke` 才能判当前训练实现 No-Go；`D5 Three-Seed-Val` 才能支持稳定性与 `Primary-Candidate`。
