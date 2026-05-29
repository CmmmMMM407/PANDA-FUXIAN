# PANDA SOTA 冲刺与论文实验总方案

最后更新：2026-05-30

## 执行状态

Round12-R15 当前作用域已于 2026-05-30 按 train/val-only 门控闭环：

- Round12 ensemble audit：`Diagnostic-only-No-Go-to-Round15`。Best non-oracle `panda_dwa_equal_logit` 只有 `+0.001633` Macro-F1，bootstrap 不支持稳健正收益；oracle any-correct 显示有互补上界但不能直接冻结。
- Round13 ADWA-PANDA：D3.5 梯度可行，但 D4 best ADWA `0.933331/0.933333/0.980645` 未打过 static aux 2.0、generic DWA 或 deterministic/same-budget/detached controls；不启动 D5。
- Round14 OOF utility calibration：`Round14-A-No-Go-to-B-C-current-assets`。当前没有 split-safe OOF utility target，旧 Round9 train-only/val-diagnostic utility CSV 不能作为 target；不启动 B/C。
- Round15：未启动 final freeze/test。最终 test 继续禁止打开。

详细执行结果见 `../experiment_log.md` 与 `../current_status.md`。

## 总目标

后续工作分成两条线并行推进：

1. **SOTA 冲榜线**：先用 val-only 上界诊断、跨 seed / 跨方法 logit ensemble、calibration 和冻结后一次性 test，判断现有模型资产是否足以冲最终主表。
2. **论文方法线**：围绕已经反复出现的正信号 `auxiliary supervision training dynamics`，设计一个可解释、可复现、能打过 strong controls 的单模型方法，而不是继续包装已失败的 boundary gate 或 UEA。

两条线必须共享同一条纪律：**三 seed val 通过并冻结最终配置前，不导出、不打开、不分析 test**。所有 PANDA 训练命令继续显式 `--model_name FTmodel`。

## 已有成果的再定位

| 证据来源 | 已知结果 | 后续用途 | 不再做什么 |
| --- | --- | --- | --- |
| PANDA / DAMMFND / MMDFND reproduced baselines | 两数据集三 seed 已完成，PANDA 是 strongest reproduced baseline | 作为主表基线和 ensemble 组件池 | 不混用 paper reported 数字 |
| R8-B static aux 2.0 | 三 seed 均高于 deterministic，平均 Macro-F1 delta `+0.004856`；seed42 D4 F1 `0.939837` | 作为方法线 anchor；作为冲榜线候选模型 | 不写成 Primary-Candidate，因为 seed2026 被 DWA 打穿 |
| Generic DWA | seed2026 F1/Acc `0.926826/0.926829`，强于 static aux `0.911679/0.912195` | 作为必须打过的 strong control；也作为 Anchored-DWA 的灵感 | 不把 generic DWA 本身写成我们的贡献 |
| Round9 oracle utility | oracle val utility F1/Acc/AUC `0.973959/0.973984/0.998773` | 作为上界诊断和 OOF utility calibration 的动机 | 不继续当前 train-only CUE gate |
| Round10 utility-only / entropy-only | utility-only expected utility `0.911898`，entropy-only `0.816022`，均强于 boundary-gated primary `0.773082` | 说明 utility/entropy 有上界，可作为 soft calibration 特征 | 不继续 low-margin/high-risk hard boundary gate |
| Round11 UEA | primary F1 `0.921905`，alpha0.25 接近 DWA，但 reverse utility 追平 best control | 作为反例：per-sample utility allocation 方向性不干净 | 不沿当前 UEA 续参 |
| R7/R8 boundary-risk | 可解释 hard samples，但 formal D4 被 shuffled-risk 打穿 | 只作为 error audit 特征 | 不作为 trust gate 或主训练信号 |
| Round9 stacking / Platt | final+aux stacking / Platt F1/Acc `0.954451/0.954472`，接近 original equal-sum | 作为 calibration/stacking 基线，尤其用于 ensemble 线 | 不把 calibration-only 结果包装成结构创新 |

## 核心假设

后续不再押“某个 uncertainty/risk heuristic 能单独改变 final boundary”。新的假设是：

```text
PANDA 的主要可提升空间来自 auxiliary supervision 的训练动力学和多模型误差互补。
Utility / entropy 仍有信息，但必须通过 OOF target、calibration 或 ensemble feature 使用，
不能再直接作为 hard gate 或 per-sample branch loss direction。
```

## Round12：SOTA 上界与 Ensemble 诊断

### 目标

先回答一个问题：**现有模型资产通过合理融合，val 上到底能涨多少？**

如果 ensemble oracle / simple ensemble 都没有明显空间，继续发明复杂单模型的 ROI 很低。如果 ensemble 有空间，再反推单模型方法应该学什么。

### 12-A：可用模型资产盘点

盘点并补齐以下模型在 Weibo-21 / Weibo 的 train/val logits 或 probability artifact：

- PANDA reproduced seeds `42/2024/2026`
- Static aux 2.0 seeds `42/2024/2026`
- Generic DWA seeds `42/2024/2026`，缺失则先补 train/val-only
- DAMMFND / MMDFND reproduced seeds `42/2024/2026`
- Round9 stacking / Platt 所需 final logits、aux logits、branch logits

只允许导出 train/val logits；D5 冻结前禁止 test logits。

### 12-B：Val-only ensemble 上界

按从弱到强的顺序跑：

1. Equal-weight logit average：PANDA seeds、PANDA + static aux、PANDA + DWA、PANDA + DAMMFND。
2. Validation-tuned convex weights：只在 val 上用嵌套或 leave-one-seed protocol 选权重，防止对单个 val 过拟合。
3. Calibration before ensemble：temperature / Platt / isotonic 仅作为 calibration control。
4. Oracle disagreement upper bound：只用于诊断，不作为方法结果，估计如果能选择正确模型，理论可涨多少。
5. Diversity audit：记录 pairwise error overlap、Q-statistic、disagreement correct rate、high-confidence wrong overlap。

### 12-C：Go / No-Go

`Go-to-Round15-final-freeze` 的最低要求：

- Ensemble 在 Weibo-21 val 上 Macro-F1 和 Accuracy 均超过 strongest single reproduced baseline；
- 至少两个 seed 或两个方法族带来互补，而不是单个 seed luck；
- 选权规则可复现，不使用 test，不使用样本文本泄漏特征；
- 与 single best model 的提升至少达到 `+0.002` Macro-F1 或给出 paired bootstrap 支持。

如果 simple ensemble 已显著提升，保留为冲榜线；如果只有 oracle ensemble 有空间但可学习 ensemble 不涨，则转入 Round14 OOF utility calibration。

## Round13：Anchored-DWA PANDA 单模型方法线

### 目标

把 R8-B static aux 2.0 和 DWA seed2026 反例整合成真正的 PANDA-specific 单模型方法：

```text
Static aux 2.0 提供稳定总预算 anchor；
DWA 只调 text/image/fusion auxiliary branches 的相对权重；
final CE 始终保持主导，避免 aux 动态权重吞掉 final boundary。
```

### 方法草案

候选名：`ADWA-PANDA / Anchored Dynamic Auxiliary-supervision PANDA`

核心形式：

```text
L = L_final + lambda_aux(t) * sum_b r_b(t) * L_aux_b

lambda_aux(t) = clipped schedule around static 2.0
r_b(t) = clipped DWA relative branch weights
```

约束：

- `lambda_aux(t)` 不允许无界漂移，建议范围 `[1.0, 2.5]` 或 `[1.5, 2.5]`。
- `r_b(t)` 只控制 branch 相对比例，均值归一为 1。
- 加入 final-loss guard：若 val final loss 或 final margin 退化，降低 aux 动态幅度。
- 可加 entropy smoothing，但不能使用 Round10/11 失败的 boundary hard gate。

### 13-A：D3.5 梯度 sanity

验证 Anchored-DWA 的梯度是否真实触达：

- `h_final`
- `final_classifier`
- text/image/fusion branch features
- aux heads

并比较：

- static aux 2.0
- generic DWA
- GradNorm
- PCGrad / CAGrad
- detached aux
- same-budget CE

### 13-B：D4 seed42 smoke

在 Weibo-21 seed42 跑 5 epoch train/val-only：

- `adwa_clip_1p5_2p5`
- `adwa_clip_1p0_2p5`
- `adwa_final_guard`
- `adwa_entropy_smoothed`
- controls：deterministic、static aux 2.0、generic DWA、GradNorm、PCGrad、CAGrad、detached aux、same-budget

### 13-C：D5 三 seed val

只有 D4 同时打过 static aux 2.0 和 generic DWA 才启动。

D5 要求：

- 三 seed 每个 seed 都不低于 deterministic；
- 三 seed mean 优于 static aux 2.0 和 generic DWA；
- 至少两个 seed 优于当 seed best strong control；
- flip audit W2C > C2W；
- 不使用 test 参与任何选择。

## Round14：OOF Utility Calibration 线

### 启动条件

只有满足以下任一条件才启动：

- Round12 显示不同模型/branch 有明显 oracle selection 空间；
- Round13 的 ADWA 单模型有正趋势，但 high-confidence wrong / branch disagreement 仍集中；
- 需要把 Round9 oracle utility 的上界转化成可学习机制。

### 核心修正

旧 CUE/UEA 失败的关键是 train-only utility target 泛化失败，以及 per-sample allocation 被 reverse utility control 抹平。Round14 必须改成：

```text
Out-of-fold utility target
+ calibration features
+ split-safe meta learner
+ nested validation
```

### 14-A：OOF target 构造

在 train split 内部做 K-fold：

- 每折只用 K-1 folds 训练或读取 frozen branch predictors；
- 在 held-out fold 生成 branch utility / model utility target；
- 拼接得到 train 内 OOF utility target；
- val 只用于最终诊断，不参与 target 构造。

### 14-B：Meta feature

允许使用：

- final / branch logits
- branch entropy
- branch disagreement
- calibrated confidence
- PAD/source metadata
- training-time loss trajectory summary

禁止使用：

- test 样本
- test label
- 样本文本明文特征作为 meta shortcut
- val label 反向构造 target

### 14-C：候选输出

两种输出形态：

1. **Utility-calibrated ensemble**：作为冲榜线；
2. **Utility reliability regularizer**：作为单模型附加线，只在 ADWA 过 D4 后挂载。

### 14-D：Go / No-Go

必须打过：

- Platt / temperature
- final+aux stacking
- confidence-only gate
- shuffled utility
- reverse utility
- random utility
- static aux 2.0
- generic DWA

否则只写为 diagnostic，不进入 final freeze。

## Round15：冻结配置与最终 test 协议

只有 Round12/13/14 至少一条线完成三 seed val，并且写明最终配置，才允许进入 Round15。

冻结内容：

- 模型族与 seed 列表
- ensemble 权重或单模型超参
- calibration 方法
- early stopping / epoch
- preprocessing
- checkpoint 选择规则
- 最终报告模板

最终 test 只允许执行一次。如果 test 结果不理想，不允许回头改权重、阈值、seed、aux weight 或 ensemble 成员。

## 论文叙事结构

若 Round12 ensemble 最强：

```text
Reproducible evaluation + auxiliary dynamics diagnosis + robust ensemble for multimodal fake news detection
```

贡献写法：

1. 复现 PANDA / DAMMFND / MMDFND，建立可信 reproduced baseline。
2. 系统诊断 PANDA 的辅助监督、utility、boundary-risk 与 calibration。
3. 发现 auxiliary supervision dynamics 和 cross-seed/method diversity 是主要可提升来源。
4. 提出 split-safe ensemble / calibration protocol，并在冻结 test 上验证。

若 Round13 ADWA 最强：

```text
Anchored dynamic auxiliary supervision for PANDA-style multimodal fake news detection
```

贡献写法：

1. 指出 static aux 与 generic DWA 分别代表稳定总预算和动态分支平衡。
2. 提出 ADWA-PANDA：固定辅助监督总预算 anchor，动态调节 branch 相对权重。
3. 用 strong controls 证明不是普通 DWA / GradNorm / PCGrad artifact。
4. 用 error audit 解释改善来自哪些 branch conflict / hard cases。

若 Round14 utility calibration 成功：

```text
Split-safe counterfactual utility calibration for branch evidence aggregation
```

贡献写法：

1. 证明 oracle utility 有高上界，但 naive train-only gate 失败。
2. 提出 OOF utility target，解决 utility target 泛化和泄漏问题。
3. 在 calibration / stacking / random / reverse utility controls 下验证有效性。

## 统一实验纪律

- 所有新实验先写 manifest。
- 所有训练默认 train/val-only。
- D5 前不导出 test logits、不打开 test label、不用 test 做任何选择。
- 所有 PANDA 命令显式 `--model_name FTmodel`。
- 每个候选必须报告 deterministic、static aux 2.0、generic DWA、GradNorm、PCGrad、CAGrad、detached aux、same-budget controls。
- 冲榜线可以使用 ensemble，但必须和单模型方法线分开叙事。
- No-Go 结果继续记录，不能删改历史证据。
