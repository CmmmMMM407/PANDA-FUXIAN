# Round 3 PANDA 方法候选：Branch-Boundary Residual

日期：2026-05-26

状态说明（2026-05-28 更新）：Round 3 branch-boundary residual 已归档为 `No-Go for current D3 offline branch-boundary residual gate`。Round 6/7 当前作用域验证已闭环且无 `Primary-Candidate`；新的待执行规划入口为 Round 7，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 和 `round7_candidate_registry.md`。验证深度复审后，R3-D training-time endogenous branch residual 是 `Not-Unlocked`，不是已通过 D4 证明失败；若未来重开，必须新 manifest + D4 seed42 training smoke。

## 定位

Round 2 已完成全部最小 gate，但没有 `Primary-Candidate`：

- P2-A reliability-conditioned final-boundary correction：`No-Go for current D3 reliability-conditioned offline final-boundary correction`。
- P2-B reliability adapter：`No-Go for current D3 reliability adapter`；aux-logit residual 只保留为 `Feasible-B` weak signal。
- P2-C actual domain-conditioned expert offline pre-screen：`No-Go for current D3 offline/pre-screen`；trained domain MoE 未被排除。
- P2-D source-utility residual：`No-Go for current D3 source residual`；differentiable source mixture 未被排除。

唯一保留的弱信号是 P2-B 的无 reliability `final+aux logits` residual adapter：Weibo-21 seed42 val F1/Acc `0.959346/0.959350`，高于 original final score `0.956086/0.956098`。这只能标记为 `Feasible-B`，不能直接写成方法成功。

Round 3 的目标是重新定义并严格审计这个弱信号：

```text
PANDA 的 text / image / fusion auxiliary heads 受到标签监督，
可能编码了 branch-level predictive cues。
Round 3 只验证这些 cues 是否能在强对照下解释 final-boundary mismatch；
在 gate 通过前，不把它写成已确认的 branch-boundary mechanism。
```

当前题眼不再是 reliability/source-domain utility，而是：

```text
branch-final boundary mismatch
```

## 核心风险

### 最大审稿攻击

这条线最容易被说成：

```text
普通 stacking / late fusion / calibration / supervised post-hoc combiner
```

因此 Round 3 不能只报告 `final+aux logits` adapter 提升。必须证明：

1. 它不是 Platt / temperature / threshold tuning。
2. 它不是 logistic stacking / weighted average。
3. 它不是参数更多或 random feature 带来的偶然增益。
4. 它不是 seed42 单点。
5. 它的收益定位在 branch-final mismatch 或 final-boundary margin 样本上。
6. 它最终能转成训练期内生模块，而不是只停在 post-hoc adapter。

## 方法命名候选

优先命名：

```text
Branch-Boundary Residual PANDA
```

备选：

- Auxiliary-to-Final Boundary Residual
- Branch-Residual Boundary Alignment
- Boundary-Conditioned Branch Residual Adapter

避免命名：

- calibration
- stacking
- logit ensemble
- auxiliary classifier fusion
- reliability-aware
- source utility

## PANDA 模块链路依据

PANDA 的 final head 不是直接吃辅助分支 logits：

- `text_classifier/image_classifier/fusion_classifier` 是三条 branch feature 上的辅助监督头。
- forward 中导出 `text_fake_news_logits/image_fake_news_logits/fusion_fake_news_logits` 以及 sigmoid 后的 `p_text/p_image/p_fusion`。
- `h_di = text_features + image_features + fusion_features`。
- PAD/GNS/DCA 生成 `h_collab`。
- `final_classifier_panda([h_di, h_collab])` 输出 final score。

因此 Round 3 的待验证解释不是“把四个分类器投票”，而是：

```text
aux heads 约束了 text/image/fusion branch 的判别方向；
final head 看到的是聚合后的 h_di 和 h_collab；
branch logits 中可能保留了 final head 没有显式吸收的 boundary projection。
```

需要继续确认的本地/远端证据路径：

- `remote_panda_work/model/PANDA.py`：确认 aux heads、`h_di`、DCA、`final_classifier_panda([h_di,h_collab])` 的 forward 链路。
- `tools/export_panda_extended_diagnostics.py`：确认 `y_score/p_text/p_image/p_fusion` 只由模型 forward 导出，不含 label-derived feature。
- `tools/run_panda_p2b_boundary_adapter_smoke.py`：确认 P2-B 只读 train/val、test 只检查存在；确认 `adapter_final_aux_residual`、`adapter_final_reliability_residual`、random/parameter controls 的 feature 构造。
- `remote_panda_work/repro_logs/p2b_boundary_adapter_smoke/`：确认 `adapter_final_aux_residual` 的 val F1/Acc 与 delta。

## Round 3 最小候选拆法

注意：这里的 `R3-A/B/C/D` 是 Round 3 候选编号，不是历史 `R3-PANDA Regret Router`。

### R3-A：AuxLogitResidual

输入：

```text
z_final, z_text, z_image, z_fusion
```

输出：

```text
z_new = z_final + g_i * delta_i
```

其中：

- `delta_i` 是由 branch logits / branch-final gaps 预测的轻量残差。
- `g_i` 是边界门控，优先在 low final-margin 或 high branch-final mismatch 样本上开启。
- residual 幅度必须受限，默认保持 original final decision。
- branch logits 默认 detach，避免把它写成额外大模型。

第一版只允许轻量线性或小 MLP，不引入大模块。核心是复核 P2-B `adapter_final_aux_residual` 是否跨 seed 稳定。

重要约束：

- raw `final+aux logits` adapter 只能作为 ordinary combiner / stacking control，不直接作为主方法。
- 真正候选必须是 boundary-gated residual，只在 low final-margin 或 high branch-final mismatch 区域开启。
- 必须报告 residual sparsity、gate activation rate、high-margin correct flip rate。
- 若 logistic stacking、weighted average 或 unconstrained final+aux MLP 达到同等或更好结果，当前 R3-A D3 offline boundary-gated residual candidate No-Go；training-time endogenous branch residual 仍为 `Not-Unlocked`，需新 manifest + D4。

### R3-B：BranchDisagreementResidual

输入从 raw aux logits 改为 branch gap/std/mean：

```text
delta_i = f(z_text-z_final, z_image-z_final, z_fusion-z_final,
            z_text-z_image, aux_std, aux_mean)
g_i = 1[margin(z_final) < tau] 或 soft gate
```

目标是验证“branch-final mismatch / branch disagreement”是否比原始 aux logits 更可解释。

### R3-C：BranchDrop Attribution

同一训练协议下做 branch 归因：

- final + text。
- final + image。
- final + fusion。
- final + text + image。
- final + text + fusion。
- final + image + fusion。
- final + all aux。

目标是确认收益来自某个 branch、某种组合，还是 branch disagreement 结构。

### R3-D：Training-time Endogenous Branch Residual

若 R3-A/B 过线，必须验证训练期内生版本：

- final head 接收 detached branch logits 或 branch residual tokens。
- residual path 有幅度正则和 boundary mask。
- 第一版仍冻结 backbone，只训练极小 head。
- 和 offline adapter 使用同一套 train/val 决策规则。

没有训练期内生版本时，不升级为主方法。

## 必须补的 Controls

### Calibration / stacking controls

- final-only Platt scaling。
- temperature scaling。
- isotonic / threshold tuning。
- logistic regression stacking。
- simple weighted average of final/text/image/fusion logits。
- final-only MLP。
- domain bias / category one-hot control。

### Parameter / random controls

- parameter-matched MLP，只吃 final。
- final + random features。
- final + shuffled aux logits。
- final + permuted branch identities。
- duplicate-final logits。

### Branch attribution controls

- final + text only。
- final + image only。
- final + fusion only。
- final + text/image。
- final + text/fusion。
- final + image/fusion。
- branch confidence only。
- branch disagreement only。
- branch gap/std only。
- branch-drop attribution。

### Boundary localization controls

- low final-margin bin。
- high final-margin bin。
- high branch-final disagreement bin。
- low branch-final disagreement bin。
- weak-domain bins。
- high-confidence original-correct samples。

### Leakage controls

- adapter 输入严禁包含 `y_true/is_error/is_high_conf_error`。
- 不能使用 val label 选择 threshold、弱域定义或 branch subset。
- 弱域仍只能由 train/val baseline 规则预先固定。
- test 只在 config 冻结后 confirmatory。
- Round 3 gate scripts 不加载 test predictions、不导出 test split、不检查 test metrics；test 只能在三 seed val 与 primary config 完全冻结后作为一次性 confirmatory report。

## Round 3 Gate 顺序

1. Protocol freeze：固定 `allowed_splits=train/val`、features、normalization、candidate list、controls、metrics 和 No-Go 线；manifest 必须记录 `test_split_exported=false`、`test_used_for_decision=false`。
2. Evidence / leakage audit：确认 aux logits 只来自 PANDA forward，不含 `y_true/is_error/is_high_conf_error`；threshold、弱域和 branch subset 不用 val/test label 调。
3. Calibration moat：original final、final-only Platt、temperature、isotonic、train-only threshold tuning、final-only MLP、domain/category bias control。
4. Ordinary combiner moat：logistic stacking、weighted average final/text/image/fusion logits、unconstrained final+aux MLP、duplicate-final logits。若这些同样达到提升，Round 3 不得升级。
5. Random / parameter controls：parameter-matched final-only MLP、final+random features、final+shuffled aux logits、branch identity permutation、sample shuffle seeds。
6. Branch mechanism gate：single-branch、branch-pair、branch disagreement only、branch gap/std only、raw aux vs gap feature 对比；必须做 low-margin / high-mismatch bin 和 flip audit。
7. Seed42 gate：只用 train 拟合、val 决策；val F1/Acc 不低于 original/deterministic，最好达到 P2-B weak signal；且必须打过上述 controls。
8. Freeze primary config：seed42 过线后冻结 exact variant、feature set、threshold、gate tau、head size 和 regularization，不再补参。
9. 三 seed val：复核 seeds 42/2024/2026；seed2024 不允许强负例；每个 seed 不低于 original/deterministic，三 seed mean 最好 `>= +0.3pp`。
10. R3-D endogenous check：没有训练期内生 residual 版本，只能是 offline evidence，不能升 `Primary-Candidate`。
11. Weibo expansion / final test：Weibo-21 三 seed val 过后才扩 Weibo；所有 val 决策完成后 test 只做 confirmatory。

## 必须报告的诊断

1. Flip audit：
   - wrong -> correct。
   - correct -> wrong。
   - near-boundary flip。
   - high-confidence flip。

2. Residual audit：
   - residual magnitude distribution。
   - residual sparsity / gate activation rate。
   - residual by final-margin bin。
   - residual by branch-final disagreement bin。
   - residual by domain。

3. Boundary-bin gain：
   - low margin bin F1/Acc。
   - high mismatch bin F1/Acc。
   - weak-domain F1。
   - high-confidence error rate。

4. Fair comparison：
   - same train/val splits。
   - no test-based tuning。
   - config frozen before any test confirmatory。

## Go / No-Go 标准

### Seed42 最小 gate

通过线：

- val F1/Acc 不低于 original final score `0.956086/0.956098`。
- 最好达到或超过 P2-B weak signal `0.959346/0.959350`。
- 打过 Platt / temperature / threshold tuning。
- 打过 logistic stacking / weighted average。
- 打过 final-only MLP、random-feature、shuffled-aux、duplicate-final controls。
- 打过 branch identity permutation 和 branch-drop negative controls。
- low-margin 或 high branch-final disagreement bin 有净收益。
- wrong->correct 明显多于 correct->wrong。
- ECE/Brier/HCE 不能大幅恶化；若恶化，必须有明确边界收益解释。
- residual 不能表现为全局常数 bias；需要报告 magnitude、sparsity/gate activation 和 boundary-bin 分布。

No-Go：

- 提升被 calibration / stacking / weighted average 同样达到。
- 只在某一个 domain 或类别上偶然提升。
- residual 是全局 bias，而不是 boundary-localized correction。
- high-confidence correct 样本被大量翻错。

### 三 seed val 复核

进入 seeds 2024/2026 的条件：

- seed42 过所有强对照。
- gate config 固定，不再补 threshold、lambda、feature set。

三 seed通过线：

- Weibo-21 三 seed val mean F1/Acc 至少提升 `>=0.3pp`。
- 每个 seed 不低于 original/deterministic。
- seed2024 不允许出现强负例。
- boundary-bin / flip audit 方向一致。
- 至少一个 branch attribution 解释稳定，不允许每个 seed 的“贡献 branch”完全漂移。

### 扩 Weibo 条件

- Weibo-21 三 seed val 通过后才扩 Weibo。
- Weibo 三 seed至少不掉点，最好平均提升 `>=0.2pp`。
- 若 Weibo 不提升但不退化，论文主张必须收敛为 Weibo-21 confirmed + Weibo boundary-conditioned analysis。

## 写作边界

可以写：

```text
PANDA's auxiliary modality branches may encode branch-level predictive cues that the final classifier does not explicitly consume. We test whether a constrained branch-boundary residual path can improve final-boundary mismatch regions beyond calibration, stacking, and random controls.
```

不能写：

```text
We improve PANDA by stacking auxiliary classifiers.
```

不能把 Round 3 写成 reliability/source-domain adaptation 成功。它是一个新的 branch-boundary 方法候选。

## 当前决策

Round 3 已完成 seed42 train/val control moat，判定当前 `D3 offline branch-boundary residual gate` 为 `No-Go`，不能进入正式主线。

当前状态：

```text
No-Go: current D3 offline branch-boundary residual seed42 gate
No Primary-Candidate yet
```

2026-05-26 gate 结果：

- 已建立 clean train/val-only 输入目录 `remote_panda_work/repro_logs/round3_branch_boundary_trainval_input/`，manifest 记录 row count、SHA、`test_split_exported=false` 和 `test_used_for_decision=false`。
- 已生成 `remote_panda_work/repro_logs/round3_branch_boundary_gate_seed42/round3_branch_boundary_protocol_manifest.json` 与 `round3_branch_boundary_leakage_audit.json`；leakage audit 通过，forbidden columns 未作为特征使用。
- Original final score val F1/Acc/AUC `0.956086/0.956098/0.987382`。
- Best primary `r3b_gap_boundary_gated_residual` val F1/Acc/AUC `0.949593/0.949593/0.987171`，低于 original；wrong->correct 3，correct->wrong 7。
- Best control `weighted_average_final_aux_logits` val F1/Acc/AUC `0.956093/0.956098/0.987499`，匹配/打穿 best primary。
- Boundary localization 未成立：best primary low-margin delta F1 `-0.008849`，high-mismatch delta F1 `-0.005663`。

决策：

- 不复核 seeds 2024/2026。
- 不扩 Weibo。
- 不启动本轮 R3-D training-time endogenous branch residual；该训练期版本为 `Not-Unlocked`，若重开必须新 manifest + `D4`。
- P2-B `final+aux logits` residual adapter 降级为 current D3 offline ordinary-combiner risk evidence。

test 仍未用于本轮决策。
