# PANDA 复现实验阶段报告

日期：2026-05-22

更新说明（2026-05-28）：本文仍是复现实验阶段报告，只记录 reproduced baseline 和 paper-aligned 复现结论；当前创新执行入口见 `current_status.md` 和 `todo.md`，Round 7 历史规划已归档到 `docs/archive/method_rounds/新创新方案_Round7PANDA_RiskAwareFinalBoundary.md` 与 `docs/archive/registries/round7_candidate_registry.md`。

更新说明（2026-05-24）：本文是 PANDA 复现阶段报告，保留当时与 paper reported baseline 对比的历史口径。后续已补齐 MMDFND / DAMMFND 两数据集三 seed reproduced baseline；创新论文主表应使用 reproduced baseline，具体数值以 `current_status.md`、`todo.md` 和 `remote_panda_work/repro_logs/*_diagnostics/overall_metrics_summary.csv` 为准。

## 结论摘要

本阶段已完成 PANDA 在 Weibo-21 与 Weibo 两个中文多模态多领域假新闻检测数据集上的 paper-aligned 三 seed 复现。实验使用官方 PANDA commit `03e4c003e83480fe94ac52120522b34e4224f17b`，显式进入 `--model_name FTmodel` 分支，参数对齐论文设置：batch size 32、learning rate `1e-4`、epoch 50、early stop 6，seeds 为 42、2024、2026。

核心结果是：AUC 与论文报告基本对齐，Macro-F1 与 Accuracy 稳定低于论文 reported PANDA 约 0.95 到 1.16 个百分点。由于三 seed 中 seed 42 明显更高，单 seed 结果会高估复现稳定性；正式结论应优先采用三 seed mean ± sample std。

## 实验环境与代码边界

- 远端平台：AutoDL，单张 NVIDIA GeForce RTX 4090 24GB。
- 远端环境：Python 3.10.8，PyTorch 2.1.2+cu118，CUDA 可用。
- 官方代码：`https://github.com/lu-wayne/panda`，commit `03e4c003e83480fe94ac52120522b34e4224f17b`。
- 参考环境与数据链路：MMDFND 参考仓库 commit `a8a79b776845fc684d0269f5341235c0b1ea5c02`。
- 关键入口：必须使用 `python main.py --model_name FTmodel`，否则默认 `clean_vib` 不是 PANDA。
- 权重 sanity：RoBERTa、MAE、CN-CLIP 权重已记录 hash manifest；MAE checkpoint 与 CN-CLIP embedding sanity 均通过。

## 兼容补丁说明

本复现使用两类最小 code-compat patch，只解决当前官方代码在 Python 3.10 / 当前依赖环境下的运行阻断，不改变 PANDA 算法路径。

1. `model/PANDA.py` 兼容补丁：接收 `dataset_type` 参数；修复共享专家列表在赋值前被 `.append()` 的问题；修复 `save_param_dir` 首次创建时被写成 `None` 的问题。证据文件：`remote_panda_work/repro_logs/20260521_code_compat_patch.diff`。
2. `utils/utils.py` 指标补丁：将 sklearn 返回的 Python float 从 `.round().tolist()` 改为 `round(float(...), 4)`，避免验证阶段报错。证据文件：`remote_panda_work/repro_logs/20260521_metrics_float_patch.diff`。

这两项补丁属于 code-compat patch，不属于 diagnostic patch；所有主表结果均基于同一兼容补丁链路。

## Sanity Gate

- Weibo-21 数据校验：train/val/test 为 4926/615/615；xlsx、普通图片 pkl、CLIP 图片 pkl 第一维一致；图片命中率为 100%。
- Weibo 数据校验：train/val/test 为 5415/843/1465；普通图片 pkl 与 CLIP 图片 pkl 第一维一致。
- Weibo-21 小 batch forward：主输出、text/image/fusion 辅助输出、`loss_rec` 均 finite，主输出非全常数。
- Weibo 小 batch forward：主输出、text/image/fusion 辅助输出、`loss_rec` 均 finite，主输出非全常数。
- Gumbel/PANDA 随机性 sanity：固定 seed 重复 forward 一致，换 seed 后主输出与 neighbor selection 变化。因此预测导出前均固定对应 seed。

## 三 Seed 主表

### Weibo-21

| Seed | Macro-F1 | Accuracy | AUC | Support |
| --- | ---: | ---: | ---: | ---: |
| 42 | 0.9545 | 0.9545 | 0.9886 | 615 |
| 2024 | 0.9480 | 0.9480 | 0.9887 | 615 |
| 2026 | 0.9398 | 0.9398 | 0.9863 | 615 |
| Mean ± sample std | 0.9474 ± 0.0073 | 0.9474 ± 0.0073 | 0.9879 ± 0.0014 | 615 |

对应证据：

- `remote_panda_work/repro_logs/20260521_weibo21_three_seed_summary.json`
- `remote_panda_work/repro_logs/20260521_weibo21_three_seed_summary.csv`
- `remote_panda_work/repro_logs/20260521_weibo21_seed*_test_metrics.json`
- `remote_panda_work/repro_logs/20260521_weibo21_seed*_test_predictions.csv`

### Weibo

| Seed | Macro-F1 | Accuracy | AUC | Support |
| --- | ---: | ---: | ---: | ---: |
| 42 | 0.9447 | 0.9447 | 0.9868 | 1465 |
| 2024 | 0.9379 | 0.9379 | 0.9854 | 1465 |
| 2026 | 0.9420 | 0.9420 | 0.9875 | 1465 |
| Mean ± sample std | 0.9415 ± 0.0034 | 0.9415 ± 0.0034 | 0.9866 ± 0.0011 | 1465 |

对应证据：

- `remote_panda_work/repro_logs/20260521_weibo_three_seed_summary.json`
- `remote_panda_work/repro_logs/20260521_weibo_three_seed_summary.csv`
- `remote_panda_work/repro_logs/20260521_weibo_seed*_test_metrics.json`
- `remote_panda_work/repro_logs/20260521_weibo_seed*_test_predictions.csv`

## 与论文报告结果对比

PANDA 论文 Table 1 报告的主表结果来源于 AAAI 2026 论文页面与 PDF：`https://ojs.aaai.org/index.php/AAAI/article/view/37049`。

| Dataset | Method | F1 | Acc | AUC | 备注 |
| --- | --- | ---: | ---: | ---: | --- |
| Weibo | MMDFND reported | 0.933 | 0.933 | 0.973 | PANDA paper Table 1 |
| Weibo | DAMMFND reported | 0.941 | 0.944 | 0.979 | PANDA paper Table 1 |
| Weibo | PANDA reported | 0.951 | 0.953 | 0.987 | PANDA paper Table 1 |
| Weibo | 本复现 PANDA mean | 0.9415 | 0.9415 | 0.9866 | 三 seed 独立重算 |
| Weibo-21 | MMDFND reported | 0.940 | 0.940 | 0.976 | PANDA paper Table 1 |
| Weibo-21 | DAMMFND reported | 0.943 | 0.946 | 0.979 | PANDA paper Table 1 |
| Weibo-21 | PANDA reported | 0.958 | 0.959 | 0.988 | PANDA paper Table 1 |
| Weibo-21 | 本复现 PANDA mean | 0.9474 | 0.9474 | 0.9879 | 三 seed 独立重算 |

相对 PANDA reported：

- Weibo-21：Macro-F1 低 0.0106，Accuracy 低 0.0116，AUC 低 0.0001。
- Weibo：Macro-F1 低 0.0095，Accuracy 低 0.0115，AUC 低 0.0004。

相对可复现 baseline 的 reported 主表：

- Weibo-21：本复现 PANDA mean 高于 MMDFND 和 DAMMFND 的 F1/Acc/AUC，仍能支撑 PANDA 相比前代方法有优势；但低于 PANDA 论文自身 reported F1/Acc。
- Weibo：本复现 PANDA mean 的 AUC 高于 MMDFND/DAMMFND reported，F1 与 DAMMFND reported 基本持平，Accuracy 略低于 DAMMFND reported 0.0025。

## 复现差异分析

1. Seed 波动不可忽略。Weibo-21 seed 42 的 Macro-F1 为 0.9545，接近论文 0.958；seed 2026 降至 0.9398。单 seed 或最佳 seed 不应作为最终复现结论。
2. AUC 对齐而 F1/Acc 偏低，说明排序能力基本复现，但固定 0.5 阈值下的分类边界、checkpoint 选择或评估前向随机性可能导致离散标签指标下降。
3. PANDA eval 路径仍包含 Gumbel neighbor selector 随机性。本项目在预测导出前固定 seed，但训练日志中的最终 test 与独立导出的 test AUC 存在小幅差异，符合该机制预期。
4. 官方代码需要兼容补丁才能完成运行。补丁未改变模型公式，但它意味着复现实验不是 pristine official commit 一键运行，报告中必须单独说明。
5. Weibo 与 Weibo-21 数据路径、pkl 预处理和 CLIP 图片 pkl 均已做一致性检查，因此当前主要差异更可能来自随机性、实现细节和论文未完全公开的训练/选择细节，而不是明显的数据错位。

## 最终判断

PANDA 在两个中文数据集上的主实验已经完成可追溯复现。复现结果支持以下结论：

- PANDA 的 AUC 几乎完全复现论文 reported 水平。
- PANDA 相比 MMDFND/DAMMFND 的优势在 Weibo-21 上仍成立。
- Weibo 上本复现 PANDA 的 F1/Acc 未稳定超过 DAMMFND reported，但 AUC 仍接近论文 PANDA reported。
- 论文 PANDA reported 的 F1/Acc 在当前 official commit + code-compat patch + 三 seed 设置下没有完全复现，差距约 1 个百分点。

后续增强结论可信度的原始优先级如下；其中第 3、4 项已在 2026-05-24 基本完成：

1. 补跑更多 seeds 或复核论文是否采用最佳 seed/单 seed 主表。
2. 固定或记录 Gumbel neighbor selection，比较 deterministic eval 与当前随机 eval。
3. 复现 DAMMFND/MMDFND 官方代码，而不是只引用 reported baseline。（已完成两数据集三 seed。）
4. 做 per-domain error analysis。2026-05-23 后续复核更新的弱域结论为：Weibo-21 重点看科技、医药健康、社会生活；Weibo 重点看政治、科学、军事。本文旧版英文域名提示仅为阶段性方向，后续以 `current_status.md` 和 gate 文档为准。（已生成 per-domain/error/reliability 诊断。）

## 参考来源

- PANDA AAAI 2026 论文页面：`https://ojs.aaai.org/index.php/AAAI/article/view/37049`
- PANDA PDF：`https://ojs.aaai.org/index.php/AAAI/article/download/37049/41011`
- PANDA 官方代码：`https://github.com/lu-wayne/panda`
- MMDFND 参考代码：`https://github.com/yutchina/MMDFND`
- DAMMFND 参考代码：`https://github.com/luweihai/DAMMFND`
