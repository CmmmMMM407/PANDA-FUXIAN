# Round 6 候选登记表

日期：2026-05-28

状态：`Round6-Current-Scope-Closed / No-Primary-Candidate / Validation-Depth-Audit`。R6-A 已从非训练 readiness 推进到正式 `FROZEN_SMOKE` seed42 train/val-only D4 smoke，并完成 19 个 variants；当前训练实现判定 `No-Go`，best primary `r6a_late_aux_ramp_0p5_to_2p0` F1/Acc `0.938184/0.938211`，低于 best control `static_aux_weight_2p0_anchor_control` 的 `0.939837/0.939837`。Round 6/7 当前应跑验证已闭环：R6-B/R6-E/R6-F/R6-I 当前 frozen/offline 变体 `No-Go`，R6-C 三 seed offline 复核不稳定，R6-D cross-architecture complementarity `No-Go`，R6-G/R6-J direct D2/D3 frozen probes `No-Go`，R6-H frozen prompt-response `No-Go`。当前没有 `Primary-Candidate`，不复核 seeds、不扩 Weibo、不导出/打开/分析 test。验证深度详见 `创新方法验证深度复审.md`：`D0/D1` 只能支持 Evidence-only / Blocked / Provisional，`D2/D3` 只能否定当前 frozen/offline/proxy 变体，训练期方法至少需要 `D4 Seed42-Smoke` 才能判当前训练实现 No-Go，`D5 Three-Seed-Val` 才能支持稳定性主张。

后续入口：Round 7 已另建新候选池，见 `新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 与 `round7_candidate_registry.md`。Round 7 不继承本登记表里的 `No-Go` 结论，只继承强对照和验证深度规则。

## 共用字段

每个候选必须补齐：

| 字段 | 含义 |
| --- | --- |
| `candidate_id` | 稳定候选编号 |
| `family` | 方法家族 |
| `hypothesis` | 第一性原理假设 |
| `code_path` | 预期改动或只读检查的代码路径 |
| `minimal_change` | 最小实现或最小检查 |
| `expected_signal` | Gate-0 应观察到的核心信号 |
| `primary_baseline` | 主要比较基线 |
| `strong_controls` | random/shuffled/same-budget/parameter-matched 等强对照 |
| `gate0_inputs` | 允许使用的数据和产物 |
| `forbidden_inputs` | 禁止使用的数据和产物 |
| `metrics` | final、branch、flip、control、cost 指标 |
| `go_rule` | Feasible-A/B 判定线 |
| `no_go_rule` | No-Go 判定线 |
| `claim_scope` | 当前结论覆盖的是 probe、offline/frozen 变体、训练实现，还是方法族 |
| `level_reached` | 当前最高验证深度：D0/D1/D2/D3/D4/D5 |
| `required_level_for_exclusion` | 若要排除当前 claim_scope 至少需要达到的验证深度 |
| `status_scope` | `No-Go` / `Blocked` / `Not-Unlocked` / `Provisional No-Go` 的适用边界 |
| `checkpoint_lifecycle` | checkpoint 保留/删除规则 |
| `promotion_rule` | 晋级 smoke、三 seed val、confirmatory test 的规则 |

## 候选 R6-A

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-A` |
| `family` | Auxiliary supervision / branch-to-final alignment；当前按 `Auxiliary Supervision Sensitivity and Alignment Probe` 降调命名 |
| `hypothesis` | 默认 mean aux BCE 的强度、分支配比和时序没有对齐 final boundary；重新平衡 aux supervision 可能比 R5-A image projection 更直接塑造 `h_di`。 |
| `code_path` | `model/PANDA.py::Trainer.train` loss 组合；`main.py/run.py` CLI 透传；诊断工具 `tools/evaluate_panda_selector_variants.py` 与 R5A telemetry。 |
| `minimal_change` | static aux sweep、aux schedule、branch-specific aux、detached/no-feature-update aux、random/shuffled aux labels、same-budget controls、generic PCGrad/CAGrad 和 random-sign controls；CLI/config/run/Trainer 的 branch-specific/schedule/detach/random/shuffled aux 基础设施已补并通过 sanity；seed42 train/val-only D4 smoke 已完成。 |
| `expected_signal` | primary final F1/Acc 不低于 deterministic；branch conflict telemetry 改善能转成 flip audit 净正，而不是只改善 ECE/Brier。 |
| `primary_baseline` | `deterministic_train_l0`、`same_budget_noop_l0`、R5A `aux_weight_2p0` 作为 control anchor；`aux_weight_2p0` 不得作为 primary。 |
| `strong_controls` | static aux sweep、random aux labels、shuffled branch-label mapping、detached aux/no-feature-update、generic PCGrad/CAGrad/GradNorm/DWA、final-only longer epoch。 |
| `gate0_inputs` | Weibo-21 seed42 train/val-only；已有 R5A telemetry；frozen/common branch diagnostics；不打开 test。 |
| `forbidden_inputs` | test split、test predictions、test-derived weak domain、根据 test 改 aux schedule 或 primary variant。 |
| `metrics` | final F1/Acc/AUC/ECE/NLL/Brier/HCE；text/image/fusion branch metrics；wrong->correct/correct->wrong；low-margin/weak-domain/HCE bins；best-control margin；wall time/GPU/epoch-to-best。 |
| `go_rule` | Feasible-A：F1/Acc 不低于 deterministic，理想 `>= +0.3pp`，且打过 best static/control，flip 净正；Feasible-B：机制有信号但主指标或 control moat 不足。 |
| `no_go_rule` | 低于 deterministic；输给 best static aux/control；只改善 calibration/telemetry；`correct_to_wrong >= wrong_to_correct`；random/shuffled/same-budget 同样有效。 |
| `claim_scope` | 当前覆盖 R6-A aux supervision rebalancing 的 seed42 5-epoch train/val-only D4 训练实现；不覆盖本质不同 aux/final-boundary 新机制，也不支持稳定性主张。 |
| `level_reached` | `D4 Seed42-Smoke`。 |
| `required_level_for_exclusion` | 当前训练实现可 D4 No-Go；若要支持跨 seed 稳定性或方法族排除，需要 `D5` 或新候选 manifest。 |
| `status_scope` | `No-Go for current R6-A D4 training implementation`：best primary 低于 best static/control，flip net 也不优于 control。 |
| `checkpoint_lifecycle` | No-Go smoke checkpoint 放可回收目录；长期只保留 manifest/summary/flip/telemetry/notes/logs/metrics，不同步 checkpoint、权重或原始数据。 |
| `promotion_rule` | 本轮不晋级三 seed val，不扩 Weibo，不看 test。未来若重开，必须提出本质不同候选并新建 manifest；不得把 static aux/control 现象包装成 R6-A 成功。 |

## 候选 R6-B

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-B` |
| `family` | Evidence-gated branch aggregation |
| `hypothesis` | `h_di = h_text + h_image + h_fusion` 裸相加太粗；应按 branch confidence、entropy、disagreement 和 sample uncertainty 决定三条 branch evidence 权重。 |
| `code_path` | `model/PANDA.py::forward` 中 `text_features/image_features/fusion_features` 与 `h_di` 生成处；offline branch-logit diagnostics。 |
| `minimal_change` | frozen train/val 先做极小 branch weight gate；若解锁，再用 `h_evidence = w_t h_text + w_i h_image + w_f h_fusion` 替换等权相加。 |
| `expected_signal` | low-margin/high-disagreement 样本有局部收益，且 final F1/Acc 不低于 original。 |
| `primary_baseline` | original equal-sum `h_di`、deterministic final。 |
| `strong_controls` | scalar weight、logistic stacking、final+aux weighted average、Platt/temperature、shuffled-confidence、random-confidence。 |
| `gate0_inputs` | train/val frozen branch/final predictions and features only。 |
| `forbidden_inputs` | test split；根据 test 选 gate threshold/weights。 |
| `metrics` | final + branch + flip audit + low-margin/high-disagreement bins + control moat。 |
| `go_rule` | final 不降，局部 bin 净收益，且 ordinary stacking/Platt/shuffled confidence 均落后。 |
| `no_go_rule` | 只改善 calibration；ordinary stacking 或 shuffled/random confidence 追平；low-margin 无收益。 |
| `claim_scope` | 当前只覆盖 proxy branch-logit 与 feature-level frozen final-head evidence gate。 |
| `level_reached` | `D2/D3`。 |
| `required_level_for_exclusion` | 若要排除 learned branch aggregation 训练实现，需要新 manifest 和 `D4`。 |
| `status_scope` | 当前 frozen/proxy 变体 No-Go；不永久否定训练期 learned aggregation。 |
| `checkpoint_lifecycle` | Gate-0 无 checkpoint；smoke checkpoint 可回收。 |
| `promotion_rule` | Gate-0 过线后才写 branch evidence gate smoke manifest。 |

当前审计注记：已跑 proxy branch-logit 与 feature-level frozen final-head Gate-0，二者均 No-Go；该结论只覆盖当前 frozen/proxy evidence-gate 变体，不永久否定所有训练期 branch aggregation。

## 候选 R6-C

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-C` |
| `family` | Boundary-local lightweight calibration |
| `hypothesis` | PANDA final boundary 已强但低 margin 局部脆弱；极小 adapter 只能作为上限诊断，除非 flip audit 净正。 |
| `code_path` | frozen `h_di/h_collab/h_final` common export；offline low-margin adapter/probe。 |
| `minimal_change` | final-only logit calibration、low-margin tiny adapter、mask-vs-random mask。 |
| `expected_signal` | low-margin bin 有局部收益且 correct->wrong 不增加。 |
| `primary_baseline` | original final、deterministic final、Platt/temperature。 |
| `strong_controls` | logit bias、global Platt、random mask、same-param MLP、final+aux ordinary stacking。 |
| `gate0_inputs` | train/val frozen features only。 |
| `forbidden_inputs` | test split；test-derived low-margin threshold。 |
| `metrics` | final + flip audit + low-margin/weak-domain bins。 |
| `go_rule` | 仅当主指标不降、flip 净正、强对照落后时 Feasible-B/A。 |
| `no_go_rule` | Platt/temperature 同样有效；correct->wrong 超过 wrong->correct；主指标低于 original。 |
| `claim_scope` | 当前覆盖 seed42/2024/2026 train/val-only offline low-margin adapter diagnostic。 |
| `level_reached` | `D3` 三 seed offline replication。 |
| `required_level_for_exclusion` | 当前深度足以判定该 offline diagnostic 不稳定；若转训练方法仍需新 manifest + `D4`。 |
| `status_scope` | seed42 `Feasible-B` 弱正信号不稳定：seed2024 为负，seed2026 被 calibration/global control 打穿；只保留 low-margin diagnostic。 |
| `checkpoint_lifecycle` | 默认无 checkpoint；若后续 smoke，按可回收目录处理。 |
| `promotion_rule` | 只在所有 P0/P1 候选 Gate-0 完成后作为 fallback 排名。 |

## 候选 R6-D

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-D` |
| `family` | Cross-architecture disagreement distillation |
| `hypothesis` | PANDA 内部机制多次被 controls 打穿；若 MMDFND/DAMMFND 与 PANDA 错误互补存在，跨架构 teacher 可能提供更干净监督。 |
| `code_path` | 已有 PANDA/MMDFND/DAMMFND train/val predictions 和 metrics；offline complementarity script 待定。 |
| `minimal_change` | 先计算 oracle upper bound、teacher-correct/PANDA-wrong 覆盖率、soft logit complementarity。 |
| `expected_signal` | teacher 互补明显超过 self-distill/random teacher。 |
| `primary_baseline` | PANDA self-distill、temperature-only。 |
| `strong_controls` | random teacher、shuffled teacher logits、single-teacher controls、temperature/Platt。 |
| `gate0_inputs` | train/val predictions/logits only。 |
| `forbidden_inputs` | 根据 test 选择 teacher、temperature 或 distill weight。 |
| `metrics` | coverage、oracle delta、final F1/Acc upper bound、calibration-only controls。 |
| `go_rule` | offline complementarity 超过 random/self-distill 且不是 calibration-only。 |
| `no_go_rule` | 互补弱、teacher 需要 test 选择、temperature control 同样有效。 |
| `claim_scope` | 当前覆盖 train/val teacher artifact 下的 cross-architecture complementarity D3 gate；不覆盖 distillation 训练实现。 |
| `level_reached` | `D3 Offline-Performance-Gate`。 |
| `required_level_for_exclusion` | 当前 complementarity gate 可 No-Go；distill 训练实现若重开仍需新 manifest + `D4`。 |
| `status_scope` | `No-Go for current cross-architecture complementarity gate`：best primary 低于 PANDA original，flip `8/11` 净负。 |
| `checkpoint_lifecycle` | Gate-0 无 checkpoint；distill smoke 另建可回收目录。 |
| `promotion_rule` | Gate-0 过线后才写 distill smoke manifest。 |

## 候选 R6-E

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-E` |
| `family` | Deep supervision + early-exit diagnostic |
| `hypothesis` | aux heads 是天然 early-exit 入口；若 branch confidence 能安全分流 easy samples，同时不伤 low-margin/high-disagreement 样本，可成为效率/稳健性候选。 |
| `code_path` | `model/PANDA.py::forward` aux outputs；diagnostic export rows with p_text/p_image/p_fusion。 |
| `minimal_change` | frozen train/val 比较 always-final、always-exit、confidence-gated exit、random-exit、shuffled-confidence exit。 |
| `expected_signal` | coverage-risk 更优且 full-coverage final 不受损。 |
| `primary_baseline` | always-final deterministic。 |
| `strong_controls` | always-exit、random-exit、shuffled-confidence、max-confidence threshold、temperature/Platt。 |
| `gate0_inputs` | train/val branch/final predictions only。 |
| `forbidden_inputs` | test-derived exit threshold；只报告低 coverage 好看结果。 |
| `metrics` | coverage-risk、final metrics、low-margin bins、flip audit。 |
| `go_rule` | 在固定 coverage 或 full coverage 下打过 confidence controls。 |
| `no_go_rule` | 只筛 easy 样本；coverage 太低；random/shuffled confidence 同样有效。 |
| `claim_scope` | 当前覆盖 frozen early-exit / confidence gate full-task diagnostic。 |
| `level_reached` | `D2/D3`。 |
| `required_level_for_exclusion` | 对 inference/diagnostic 型 early-exit full-task 价值，当前深度足够；若改成训练期 deep supervision 新方法，需新 manifest + `D4`。 |
| `status_scope` | 当前 full-task early-exit diagnostic No-Go。 |
| `checkpoint_lifecycle` | 默认无 checkpoint；训练版另行冻结。 |
| `promotion_rule` | 仅当 Gate-0 显示 full-task 价值才进入 smoke。 |

## 候选 R6-F

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-F` |
| `family` | Label-preserving modality robustness |
| `hypothesis` | `h_di = h_text + h_image + h_fusion` 裸相加可能让单模态错误支配 final；同样本 view consistency 可能比跨样本替换更安全。 |
| `code_path` | `model/PANDA.py::forward` branch feature path；frozen view-delta export。 |
| `minimal_change` | text-drop/image-drop/fusion-drop frozen delta；后续只允许 label-preserving consistency。 |
| `expected_signal` | dropped-view 真实扰动 logits，且 full-view 主指标可保持。 |
| `primary_baseline` | deterministic full-view。 |
| `strong_controls` | normal dropout、R-Drop、label smoothing、random mask same-rate、same-forward-budget。 |
| `gate0_inputs` | train/val frozen forward/export。 |
| `forbidden_inputs` | 跨样本图文替换；test correctness。 |
| `metrics` | view delta、flip、branch reliance、full-view final metrics。 |
| `go_rule` | view perturbation 有解释性，且普通 dropout controls 不足以解释。 |
| `no_go_rule` | 普通 dropout 同样有效；full-view 主指标下降；consistency 抹掉有效冲突 cue。 |
| `claim_scope` | 当前只覆盖 frozen view-delta / dropped-view diagnostic。 |
| `level_reached` | `D2/D3`。 |
| `required_level_for_exclusion` | 若要排除 label-preserving consistency training，需要新 manifest + `D4`。 |
| `status_scope` | 当前 frozen view-delta 变体 No-Go；不永久否定 consistency/R-Drop/dropout 训练机制。 |
| `checkpoint_lifecycle` | smoke checkpoint 可回收。 |
| `promotion_rule` | Gate-0 过线后再冻结 consistency smoke。 |

## 候选 R6-G

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-G` |
| `family` | Soft prototype memory / EMA prototype estimator |
| `hypothesis` | 当前 hard nearest prototype 的 `torch.min + gather` 路径近似断梯度；soft assignment 或 EMA prototype bank 可能更像真实域分布估计。 |
| `code_path` | `model/PANDA.py::_calculate_pad`、`domain_prototypes`、`proto_encoder/decoder`。 |
| `minimal_change` | frozen prototype sensitivity：hard nearest、soft assignment、EMA/frozen train prototype、random prototype、class-shuffled memory。 |
| `expected_signal` | source ranking、h_collab 或 final logits 相对 random/shuffled 出现清晰边界。 |
| `primary_baseline` | current hard prototype PAD。 |
| `strong_controls` | random prototype、class-shuffled memory、bottom source、random source、same-param smoothing。 |
| `gate0_inputs` | train/val frozen features/prototypes。 |
| `forbidden_inputs` | test labels；用 test 选 prototype count/temperature。 |
| `metrics` | ranking overlap、source CE/JSD、final metrics、control moat。 |
| `go_rule` | soft/EMA prototype 明确打过 random/shuffled，且 final 不降。 |
| `no_go_rule` | 只是平滑；random/class-shuffled 同样有效；参数/内存上涨无收益。 |
| `claim_scope` | 当前覆盖 hard-vs-soft-vs-EMA/prototype sensitivity 的 direct D2/D3 frozen probe；不覆盖训练期 prototype memory。 |
| `level_reached` | `D2/D3 Direct-Mechanism-Probe / Offline-Performance-Gate`。 |
| `required_level_for_exclusion` | 当前 frozen probe 可 No-Go；训练期 prototype memory 需新 manifest + `D4`。 |
| `status_scope` | `No-Go for current direct frozen soft/EMA prototype probe`：best primary 与 original 持平且 random/shuffled controls 可匹配或更强。 |
| `checkpoint_lifecycle` | Gate-0 无 checkpoint；训练版可回收。 |
| `promotion_rule` | P2，仅在 P0/P1 无主线或 Gate-0 很强时进入 smoke。 |

当前审计注记：R6-G direct Gate-0 已补齐并判定当前 frozen soft/EMA prototype probe `No-Go`。该结论不永久排除训练期 prototype memory。

## 候选 R6-H

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-H` |
| `family` | Sample-conditioned prompt memory |
| `hypothesis` | prompt/source 若有用，应由样本 query 在 branch feature 阶段读取，而不是 late static DCA。 |
| `code_path` | `utils/*_clip_prompt.py` prompt fields、`utils.utils::clipdata2gpu`、`model/PANDA.py` prompt/DCA path。 |
| `minimal_change` | 先做接口 smoke：prompt 字段进入 model、shape 兼容、旧 checkpoint strict/partial load 策略；再做 frozen forced prompt response。 |
| `expected_signal` | sample-conditioned prompt response 的 logit/feature delta 明显强于 late DCA，并打过 random/shuffled prompt。 |
| `primary_baseline` | original late DCA。 |
| `strong_controls` | all-domain mean prompt、shuffled prompt、random prompt、same-param MLP adapter、no prompt interaction。 |
| `gate0_inputs` | train/val-only；接口/shape/frozen response。 |
| `forbidden_inputs` | 直接训练新 prompt 主线；test split。 |
| `metrics` | logit delta、JSD、CE、flip、h_prompt shift、control margin。 |
| `go_rule` | frozen response 非弱扰动且 control moat 成立。 |
| `no_go_rule` | 仍是微扰；random/shuffled prompt 同样有效；同参数 MLP 更强。 |
| `claim_scope` | 当前覆盖 prompt interface fact 与 frozen prompt-response D2/D3 probe；不覆盖可训练 prompt-memory 新模块。 |
| `level_reached` | `D2/D3 Direct-Mechanism-Probe / Offline-Performance-Gate`。 |
| `required_level_for_exclusion` | 当前 frozen prompt-response 可 No-Go；训练版 prompt memory 需新 manifest + `D4`。 |
| `status_scope` | `No-Go for current frozen prompt-response probe`：primary 低于 content baseline，flip `4/16` 净负，random/shuffled prompt controls 不支持方法主张。 |
| `checkpoint_lifecycle` | Gate-0 无长期 checkpoint。 |
| `promotion_rule` | 只有 Gate-0 过线才写训练开关。 |

## 候选 R6-I

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-I` |
| `family` | Domain-conditioned final MoE / low-rank boundary adapter |
| `hypothesis` | 现有 branch expert 不是 domain expert；若要 domain conditioning，应在 final boundary 上新增明确、极小、可控的 domain-conditioned adapter。 |
| `code_path` | `final_classifier_panda([h_di,h_collab])` 前后；可参考 MMDFND-style domain embedding/gate，但必须 parameter-matched。 |
| `minimal_change` | frozen/offline 比较 fixed final head、domain-conditioned residual、random-domain labels、same-param MLP、domain-bias-only。 |
| `expected_signal` | domain-conditioned residual 在 weak-domain/low-margin 有收益，且不被 random-domain/same-param 控制解释。 |
| `primary_baseline` | original final head。 |
| `strong_controls` | random-domain labels、same-param MLP、domain-bias-only、shared adapter、expert-collapse audit。 |
| `gate0_inputs` | train/val frozen features and category ids。 |
| `forbidden_inputs` | test-derived domains/thresholds；直接复用 task index 1 当 domain expert。 |
| `metrics` | final metrics、per-domain gains、expert usage entropy、flip audit、control moat。 |
| `go_rule` | 打过 same-param/random-domain，且 expert usage 不塌缩。 |
| `no_go_rule` | random-domain 或 same-param 追平；domain leakage 风险高；主指标不升。 |
| `claim_scope` | 当前覆盖 frozen true-domain `h_final` adapter / low-rank boundary adapter。 |
| `level_reached` | `D3`。 |
| `required_level_for_exclusion` | 若要排除全新训练期 domain-conditioned MoE，需要新 domain modules + `D4`。 |
| `status_scope` | 当前 frozen final adapter No-Go；不永久排除训练期 domain MoE 家族。 |
| `checkpoint_lifecycle` | smoke checkpoint 可回收。 |
| `promotion_rule` | P2，必须先过 P0/P1 候选对比。 |

## 候选 R6-J

| 字段 | 内容 |
| --- | --- |
| `candidate_id` | `R6-J` |
| `family` | Differentiable non-self source mixture |
| `hypothesis` | 若继续 source 路线，必须解决 self domination、hard top-k 和 free prototypes，让 final loss 可回传到 source utility。 |
| `code_path` | `model/PANDA.py::_calculate_pad`、`_gumbel_neighbor_selector`、R3 soft router path。 |
| `minimal_change` | non-self soft alpha、source utility/regret diagnostic、source adapter 作用于 `h_di`。 |
| `expected_signal` | effective source number > 1.5，non-self alpha 与负 regret 正相关，source top/bottom/random 有清晰边界。 |
| `primary_baseline` | deterministic self/source anchor、PAD-only。 |
| `strong_controls` | self-only、random non-self、bottom2、shuffled top2、same-param frozen router。 |
| `gate0_inputs` | train/val-only frozen/regret diagnostic。 |
| `forbidden_inputs` | 重复旧 R3 self-collapse 路线；test tuning。 |
| `metrics` | route entropy、self weight、alpha-regret corr、final metrics、control margin。 |
| `go_rule` | non-self utility 真实且不塌缩，final 不低于 deterministic。 |
| `no_go_rule` | self collapse；random/shuffled 打穿；final 指标下降。 |
| `claim_scope` | 当前覆盖 self-suppressed non-self source-mixture direct D2/D3 frozen probe；不覆盖训练期 source mixture 新实现。 |
| `level_reached` | `D2/D3 Direct-Mechanism-Probe / Offline-Performance-Gate`。 |
| `required_level_for_exclusion` | 当前 frozen source-mixture probe 可 No-Go；训练期 mixture 需新 manifest + `D4`。 |
| `status_scope` | `No-Go for current direct frozen self-suppressed non-self mixture probe`：best primary 与 original 持平，flip `0/0`，且 random/shuffled controls 可匹配或更强。 |
| `checkpoint_lifecycle` | smoke checkpoint 可回收。 |
| `promotion_rule` | P2/P3；只有 P0/P1 无可行主线且 Gate-0 成立才进入 smoke。 |

当前审计注记：R6-J direct Gate-0 已补齐并判定当前 frozen non-self mixture probe `No-Go`。该结论不永久排除本质不同训练期 source mixture。
