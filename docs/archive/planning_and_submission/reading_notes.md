# 文献与代码阅读笔记

## PANDA

全称：

Prototype-driven Asymmetric Neighbor-Domain Adaptation

论文标题：

From Blind Transfer to Wise Selection: Prototype-Driven Neighbor-Domain Adaptation for Fake News Detection

官方代码：

https://github.com/lu-wayne/panda

核心问题：

- 多领域多模态假新闻检测中，不同领域之间存在负迁移。
- 旧方法可能盲目融合所有源领域信息，把无关或冲突领域知识也引入目标领域。

核心模块：

- DMPG：Domain-aware Modal Prompt Generation
- PAD：Prototype-based Asymmetric Distance
- GNS：Gumbel-based Neighbor Selector
- DCA：Domain-Collaborative Attention

中文数据集结果：

- Weibo：F1 0.951，Acc 0.953，AUC 0.987
- Weibo-21：F1 0.958，Acc 0.959，AUC 0.988

2026-05-22 复核来源：

- AAAI 2026 论文页面：`https://ojs.aaai.org/index.php/AAAI/article/view/37049`
- PDF：`https://ojs.aaai.org/index.php/AAAI/article/download/37049/41011`
- Table 1 同时给出 MMDFND、DAMMFND、PANDA 在 Weibo、Weibo-21、FineFake 上的 overall F1/Acc/AUC。

复现注意：

- 不能只运行 README 的 `python main.py`。
- 必须显式使用 `--model_name FTmodel`。
- 数据和预训练权重需要参考 MMDFND 准备。
- 2026-05-21 核验官方 main commit：`03e4c003e83480fe94ac52120522b34e4224f17b`。
- 当前官方代码中，`run.py` 对 PANDA Trainer 传入 `dataset_type`，但 `model/PANDA.py::Trainer.__init__` 未声明该参数，可能导致构造失败。
- 当前官方 `model/PANDA.py` 中共享专家列表可能在初始化前被 `.append()` 使用，必须先做模型构造 sanity。
- `model/PANDA.py` 固定加载 `./mae_pretrain_vit_base.pth`，CN-CLIP 通过 `load_from_name("ViT-B-16", download_root="./")` 加载。
- Gumbel neighbor selector 在 forward 中引入随机性，重复 forward probe 需要固定随机源或做 deterministic 诊断。

## MMDFND

论文：

MMDFND: Multi-modal Multi-Domain Fake News Detection

官方代码：

https://github.com/yutchina/MMDFND

在本项目中的用途：

- 作为 PANDA 的环境和数据准备参考。
- 作为可复现 baseline。
- 提供 Weibo / Weibo-21 数据目录结构说明。

PANDA 论文 Table 1 reported 结果：

- Weibo：F1 0.933，Acc 0.933，AUC 0.973
- Weibo-21：F1 0.940，Acc 0.940，AUC 0.976

本次远端核验：

- 2026-05-21 clone commit：`a8a79b776845fc684d0269f5341235c0b1ea5c02`。
- README 确认 Weibo-21 完整多模态多领域数据需邮件获取，不能从仓库直接下载。
- README 确认 Weibo-21 应放在 `./Weibo_21/`，并包含 xlsx 划分文件、图片目录和预处理生成的 pkl。

关键目录结构：

```text
data/
Weibo_21/
pretrained_model/
mae_pretrain_vit_base.pth
CN-CLIP ViT-B-16 实际缓存文件需以 `load_from_name("ViT-B-16", download_root="./")` 下载结果为准
```

## DAMMFND

论文：

DAMMFND: Domain-Aware Multimodal Multi-view Fake News Detection

官方代码：

https://github.com/luweihai/DAMMFND

在本项目中的用途：

- 作为 PANDA 前一代强 baseline。
- 可与 MMDFND、PANDA 组成主要可复现对比。

中文数据集结果参考：

- PANDA 论文 Table 1 reported Weibo：F1 0.941，Acc 0.944，AUC 0.979
- PANDA 论文 Table 1 reported Weibo-21：F1 0.943，Acc 0.946，AUC 0.979

## RAMM

论文：

Retrieval-Augmented Multimodal Model for Fake News Detection

状态：

- 论文报告结果很强。
- 但论文给出的代码链接目前不可访问，GitHub 404。

本项目处理方式：

- 只作为 reported SOTA 或 related work 参考。
- 不作为可复现实验主表 baseline。

## PRCV/同档投稿口径

状态：

- 2026-05-28 最新项目口径：当前不是 Reliability-aware Disagreement PANDA，也不是 Round 5/R5-A 或 Round 6 当前变体延续；Round 6/7 当前作用域已闭环，新的规划入口是 Round 7 `Risk-Aware Final-Boundary Learning`。阅读重点转向训练期 risk weighting、disagreement-aware distillation、hard-region contrastive boundary learning 和 sample-level auxiliary curriculum。
- 2026-05-23 按 PRCV/CCF-C 口径重评后，项目创新方向先从单独 Stable-Calibrated PANDA 调整为 Conflict-aware Stable Neighbor-Domain Adaptation。
- 2026-05-24 gate 与 reproduced baseline 完成后，强 CLIP 图文冲突线降级，当前方向收口为 Reliability-aware Multimodal Disagreement Selection。
- PRCV 方向与多模态融合、多媒体内容安全、虚假内容检测、性能评测和可靠性分析更匹配。
- PRCV 2026 常规投稿公开口径已在 2026-04 中下旬截止；若没有已投稿稿件，应按 PRCV 同档会议或下一届 PRCV 规划。

来源：

- PRCV 2026 AC 学术平台页面：https://www.academicenter.com/conferences/details/PRCV2026.html
- 智源社区 PRCV 2026 征稿转发：https://hub.baai.ac.cn/view/54107
- PRCV 官网：https://www.prcv.cn/

对项目的影响：

- 单独 deterministic eval 和 threshold calibration 不够像研究贡献，容易被认为是后处理。
- CLIP-only 图文冲突证据不足，不能作为主贡献；branch disagreement、fusion uncertainty 和 reliability analysis 更适合当前证据。
- 稳定邻域选择应作为 reliable neighbor-domain adaptation 的机制之一。
- Calibration 降级为 reliability analysis，使用 ECE、Brier score、repeated eval variance 支撑。

## Reliability-aware Disagreement PANDA

状态说明（2026-05-27）：本节是历史阅读笔记。Reliability-aware Disagreement、uncertainty-aware stable-source、R3/R4/R5 相关路线均已完成 gate/smoke 且未产生 `Primary-Candidate`；后续只作为失败边界、强对照和审稿防御证据，不代表当前主线。

暂定题目：

Reliability-aware Multimodal Disagreement Selection for Multimodal Fake News Detection

核心问题：

- PANDA 根据领域原型距离选择邻域，但 domain-similar 不一定代表迁移可靠。
- 多模态分支分歧、融合不确定性和 reliability 低的样本更容易出现高置信错判或不稳定邻域迁移。
- Gumbel neighbor selector 在 eval 和跨 seed 下存在不稳定。

方法摘要：

- 使用 detach 后的 text-image branch disagreement 与 fusion uncertainty 建模轻量可靠性/分歧信号。
- CN-CLIP dissimilarity 只作为辅助特征和消融项，不作为主因果证据。
- 为每个 domain 维护 reliability/disagreement prototype。
- 用 reliability/disagreement distance 调制 PANDA 的 PAD/GNS logits。
- 训练阶段保留 Gumbel top-k，推理阶段使用 deterministic top-k 或 MC voting。
- 增加 selection margin 或 consistency loss 稳定邻域选择。

实验要求：

- Gate 已完成：CLIP-only 不强；full conflict 有效但弱于 confidence-uncertainty / fusion uncertainty。
- 后续正式方法必须证明不是 confidence-uncertainty-only 或 fusion-only 的包装。
- Branch disagreement / fusion uncertainty 有模型自反馈嫌疑，必须使用 detach，并消融 CLIP-only、branch-only、fusion-only、confidence-uncertainty-only、overconfidence-only、random control。
- 正式弱域由 train/val baseline bottom-k F1 或 top-k error rate 选择，test 只确认。
- Weibo-21 offline selector lambda=0.05，有弱机制苗头；Weibo lambda=0.0，不能过度宣称。
- 如写稳定性，需补 prediction-level repeated-forward `y_score` variance；当前只有 selector entropy/frequency。
- 统计检验优先使用 domain-stratified bootstrap 或 seed-aware bootstrap。
- MMDFND 和 DAMMFND reproduced baselines 已补齐。
- 主表使用 Weibo-21 / Weibo，三 seed mean ± std。
- 消融包括 deterministic selector、reliability-aware selector、branch-only、fusion-only、confidence-uncertainty-only、overconfidence-only、random control、stability regularization、calibration。
- 分析包括 per-domain F1、domain-to-neighbor heatmap、reliability/disagreement score 分布、高置信错例、ECE、Brier score、repeated eval variance。

## 2026-05-27：Round 6/7 阅读重点

- Deep supervision / deeply-supervised nets：支撑 R6-A 的 branch auxiliary supervision 不是事后调参，而是中间层表征塑形问题。
- Multi-task loss balancing：GradNorm、DWA、uncertainty weighting、PCGrad/CAGrad 只作为强对照或动态权重参考，不能直接包装成 PANDA 创新。
- Evidence-gated branch aggregation：优先阅读 multi-view/evidential fusion，但必须回到 `h_di = h_text + h_image + h_fusion` 是否需要样本条件加权。
- Early-exit / selective prediction：只作为 R6-E diagnostic，必须打过 max-confidence、temperature/Platt、random/shuffled exit controls。
- Prototype memory / domain adapter / MoE：重点看 collapse、random-domain、same-param、domain-shuffle controls；PANDA 当前 expert/gate 不是 9-domain expert，不能误读。
- Differentiable source mixture：若重开 source 路线，阅读重点是 self-route suppression、soft non-self mixture、source utility/regret 和 final-loss 可回传路径。

## 待补充阅读

- Weibo-21 原始数据论文或数据说明
- FND-bootstrap
- EANN-KDD18
- PANDA appendix / supplementary materials
- MMDFND 代码中的数据预处理细节

## 新阅读笔记模板

```markdown
## 论文/仓库名称

链接：

核心问题：

方法摘要：

使用数据集：

主要结果：

和本项目关系：

复现注意：

可疑点/未确认点：
```
# 2026-05-25：R3-PANDA 方法创新相关文献

## PANDA / 邻域迁移

- From Blind Transfer to Wise Selection: Prototype-Driven Neighbor-Domain Adaptation for Fake News Detection
  - URL: https://ojs.aaai.org/index.php/AAAI/article/view/37049
  - 记录：PANDA 将多领域假新闻检测中的负迁移归因于盲目融合所有 source domain，提出 DMPG、PAD、GNS 和 DCA。我们新方案不否定 PANDA，而是在其关键假设上推进：prototype similarity 不等于 supervised source utility。

## 领域泛化与负迁移

- GroupDRO: Distributionally Robust Neural Networks for Group Shifts
  - URL: https://arxiv.org/abs/1911.08731
  - 记录：强调平均准确率高的模型可能在特定 group 上失败；GroupDRO 需要正则/early stopping 才能改善 worst-group generalization。对 R3-PANDA 的启发是加入 domain / uncertainty-bin group risk，但不能把它作为唯一创新。

- DomainBed: In Search of Lost Domain Generalization
  - URL: https://arxiv.org/abs/2007.01434
  - 记录：很多 DG 方法在严格评估下不稳定，提醒我们必须保留强 deterministic baseline、多 seed 和严格 model selection。

- MLDG: Learning to Generalize: Meta-Learning for Domain Generalization
  - URL: https://arxiv.org/abs/1710.03463
  - 记录：episodic train/held-domain 思路适合做未来扩展，但 PANDA 已经很重，第一轮不宜引入二阶/近似 meta-loop。

- VREx / Risk Extrapolation
  - URL: https://arxiv.org/abs/2003.00688
  - 记录：risk variance 可作为轻量 group risk regularizer，适合作为 R3-PANDA 的可选 outer loss。

- Fishr
  - URL: https://arxiv.org/abs/2109.02934
  - 记录：gradient variance alignment 思路有启发，但离 PANDA 邻域提示机制较远，暂不作为主线。

## Soft routing / adapter

- From Sparse to Soft Mixtures of Experts
  - URL: https://arxiv.org/abs/2308.00951
  - 记录：Soft MoE 提供完全可微路由的思想，适合替换 PANDA 的 Gumbel top-S 随机选择。

- AdapterFusion
  - URL: https://arxiv.org/abs/2005.00247
  - 记录：轻量 adapter + fusion 可以把 source-specific knowledge 作为残差注入最终表示；R3-PANDA 使用 source adapter residuals 让 route 真正影响 final logits。

## 不确定性 / 证据学习 / 选择性预测

- Evidential Deep Learning to Quantify Classification Uncertainty
  - URL: https://arxiv.org/abs/1806.01768
  - 记录：Dirichlet evidence head 可把概率输出扩展为 evidence + uncertainty。适合作为 R3-PANDA 二阶段扩展，不放入第一轮 MVP。

- Trusted Multi-View Classification with Dynamic Evidential Fusion
  - URL: https://arxiv.org/abs/2204.11423
  - 记录：动态评估每个 view 的可信度并在 evidence level 融合，对 text/image/fusion 分支有启发。但第一轮先保持普通 auxiliary heads，避免方法堆叠。

- SelectiveNet
  - URL: https://arxiv.org/abs/1901.09192
  - 记录：可作为 high-confidence error / risk-coverage 备用路线。如果 R3-PANDA 主要改善 ECE/HCE 而不是 F1，可转 trustworthy selective PANDA 叙事。

# 2026-05-25：R4 与方案赛马相关外部文献补充

## PANDA / 当前 baseline 锚点

- From Blind Transfer to Wise Selection: Prototype-Driven Neighbor-Domain Adaptation for Fake News Detection
  - URL: https://ojs.aaai.org/index.php/AAAI/article/view/37049
  - 记录：PANDA 官方页面确认其核心模块为 DMPG、PAD、GNS、DCA，目标是从所有 source domain 盲目融合转向选择更有益的 neighbor domains。R4 的增量必须明确站在这个链路之后：不是再重复选择相似邻域，而是验证 non-self source-domain intervention 是否真正进入 final classifier boundary。

## 多模态 MoE / 专家路由

- Modality Interactive Mixture-of-Experts for Fake News Detection
  - URL: https://arxiv.org/abs/2501.12431
  - 记录：MIMoE-FND 强调用层级 MoE 和 interaction gating 建模模态交互。可借鉴其 gating / interaction 叙事，但当前 PANDA 项目的核心问题不是普通模态融合，而是 source-domain utility 和 final boundary 传导。

- Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer
  - URL: https://arxiv.org/abs/1701.06538
  - 记录：MoE 的 gate collapse / load balance 经验可用于审计 PANDA 的 domain gate 和 R3 route collapse。但 domain-conditioned expert gate 在本项目中更像实现修补或消融，不宜抢 R4 主线。

- Switch Transformers: Scaling to Trillion Parameter Models with Simple and Efficient Sparsity
  - URL: https://arxiv.org/abs/2101.03961
  - 记录：Switch 简化稀疏专家路由，并强调训练稳定性问题。对本项目的启发是：如果未来重开 learned routing，必须显式报告 load balance、effective source/expert number 和 collapse 诊断。

## 领域泛化 / 鲁棒风险

- In Search of Lost Domain Generalization
  - URL: https://arxiv.org/abs/2007.01434
  - 记录：DomainBed 提醒很多 domain generalization 方法在严格 model selection、多 seed 和公平调参下不稳。本项目必须保留 deterministic、old winning control、random、bottom、shuffled、self/duplicate-anchor 等强对照。

- GroupDRO: Distributionally Robust Neural Networks for Group Shifts
  - URL: https://arxiv.org/abs/1911.08731
  - 记录：worst-group generalization 需要正则和 early stopping 配合。对 R4 的启发是 `L_worst` / CVaR 可以作为二阶段 robustness ablation，不应在 forced-view primary 未成立前进入主损失。

- Out-of-Distribution Generalization via Risk Extrapolation
  - URL: https://arxiv.org/abs/2003.00688
  - 记录：V-REx 的 risk variance 思路适合解释 domain / uncertainty-bin 风险一致性，但当前只作为候选扩展，不能替代 final-logit source-view evidence。

## 不确定性 / 证据学习

- Evidential Deep Learning to Quantify Classification Uncertainty
  - URL: https://arxiv.org/abs/1806.01768
  - 记录：Dirichlet evidence head 可用于 text/image/fusion 分支的可信性建模。结合本项目已有失败规律，evidential head 只应作为 R4 过线后的 reliability extension；若只改善 ECE/Brier/HCE 而不改善 F1/Acc，应降级为可信性分析。

# 2026-05-26：Round 2/3 完成与 Round 4 方法候选池更新

- R3/历史 R4/P0-B/P1-A/P1-B/P1-C 已全部完成最小 gate，但必须按 D-level 作用域读取：R3 是当前 v0 训练实现 No-Go；历史 R4/P0-B/P1-A 是当前 D2 frozen/probe 变体 No-Go；P1-B 是 current checkpoint `Blocked/unsupported`；P1-C 是当前 D4+D5 selector 实现 No-Go。
- 当前主线不是诊断型论文，而是继续方法候选赛马；diagnostic/report 只保留为证据池、强对照和 fallback。
- Round 2 P2-A/P2-B/P2-C/P2-D 已全部完成；P2-A/P2-B/P2-C/P2-D 均按当前 D3 offline/frozen 变体读取，不能永久排除训练期 domain MoE、全新 source mixture 或新 branch-boundary 机制。无 reliability `final+aux logits` residual adapter 曾是 `Feasible-B` 弱信号，但 Round 3 强对照复核后已降级为 current D3 offline ordinary-combiner risk evidence。
- 下一轮候选转为 Round 4 First-Principle Boundary Rebuild：
  - R4-A Class-Conditional Boundary Geometry。
  - R4-D Error Subspace / Low-rank Boundary Correction。
  - R4-C Supervised Sample-Memory Boundary Patch。
  - R4-B Domain Shortcut / Invariance Boundary Audit。
- 方法设计原则：不要再只改 neighbor set，也不要把普通 `final+aux` stacking、kNN 后处理或 domain shortcut 普通正则包装成方法；必须证明新候选能解释并改变 final-boundary failure，并且不能被 calibration-only、ordinary combiner、weighted average、random/shuffled、label-shuffle、domain-shuffle 或 parameter-matched controls 解释。
