# 当前状态

最后更新：2026-05-21

## 当前阶段

阶段：Weibo-21 与 Weibo paper-aligned 三 seed 复现实验均已完成，进入结果整理、对比分析与报告撰写。

当前目标是整理 code-compat patch 说明，并撰写阶段复盘和最终复现报告。

## 当前假设

1. 单张 RTX 4090 24GB 足够复现 PANDA 在 Weibo-21 和 Weibo 上的主实验。
2. AutoDL 镜像使用 Python 3.10 + PyTorch 2.1.x + CUDA 12.1 最稳。
3. 第一阶段应先跑 Weibo-21，且必须使用 paper-aligned 参数：batch size 32，lr 1e-4，epoch 50。
4. 必须显式指定 `--model_name FTmodel`，否则默认跑到 `clean_vib`，不是 PANDA。
5. 复现成败的主要风险不在算力，而在数据集获取、预训练权重准备、代码默认参数不一致、数据路径对齐和官方当前代码的兼容性问题。

## 已确认事实

- PANDA 官方仓库：https://github.com/lu-wayne/panda
- AutoDL 已配置本机 SSH 密钥别名：`ssh panda-autodl`。
- 远端工作目录：`/root/autodl-tmp/panda_repro/panda`。
- 远端 GPU：NVIDIA GeForce RTX 4090 24GB，driver 580.105.08。
- 远端环境：Python 3.10.8，PyTorch 2.1.2+cu118，CUDA 11.8 可用。
- 已启用 AutoDL 学术加速：`source /etc/network_turbo`。
- PANDA 官方仓库已 clone，commit 为 `03e4c003e83480fe94ac52120522b34e4224f17b`。
- MMDFND 参考仓库已 clone，commit 为 `a8a79b776845fc684d0269f5341235c0b1ea5c02`。
- 依赖已安装；`cn_clip` 通过 OFA-Sys/Chinese-CLIP 官方仓库安装为 `cn-clip==1.5.1`。
- `FTmodel` 构造函数 sanity 已命中官方阻断：`Trainer.__init__()` 不接受 `dataset_type`。
- 已在远端打最小 code-compat patch：接收 `dataset_type`、修复共享专家列表 append、修复 `save_param_dir` 被 `os.makedirs()` 写成 `None`。
- patch 证据保存在远端：`repro_logs/20260521_code_compat_patch.diff`。
- mock 构造和真实权重构造均通过，PANDA 参数量记录为 514,266,705。
- RoBERTa、MAE、CN-CLIP 权重已下载并生成 hash manifest：`repro_logs/20260521_weight_manifest.txt`。
- MAE checkpoint sanity 通过：含 `model` key，150 个 tensor，关键 tensor 非零。
- CN-CLIP blank/noise image sanity 通过：embedding finite，L2 距离约 8.194。
- PANDA 依赖 MMDFND 的环境与数据准备方式。
- PANDA 自带 requirements 中固定了 `transformers==4.31.0`、`pandas==1.4.2`、`numpy==1.23.2`、`openprompt==1.0.1`。
- Python 3.11/3.12 可能和旧依赖不兼容，推荐 Python 3.10。
- 2026-05-21 核验 PANDA 官方 main 分支 commit：`03e4c003e83480fe94ac52120522b34e4224f17b`。
- 当前官方代码可能存在两个运行前阻断点：`run.py` 传入 `dataset_type` 但 `model/PANDA.py::Trainer.__init__` 不接收；`model/PANDA.py` 的共享专家列表可能在初始化前被 `.append()` 使用。
- PANDA 的 Gumbel neighbor selector 在 forward 中带随机性，重复 forward sanity 不能简单要求 eval 模式 bitwise 一致。
- RAMM 的论文代码链接目前 404，不作为可复现 baseline。
- 本项目文件夹中已有 Word 规划文档：`PANDA复现实验规划与日志规范.docx`。
- 本项目文件夹中已有官方代码审计记录：`official_code_audit.md`。
- Weibo 数据集 `data.zip` 已上传到远端并解压为 `/root/autodl-tmp/panda_repro/panda/data/`。
- 远端已建立软链接：`/root/autodl-tmp/panda_repro/panda/Weibo -> data`，对齐 PANDA `run.py` 的 Weibo 路径。
- Weibo 数据校验通过：train/val/test 行数分别为 5415/843/1465，普通图片 pkl 与 CLIP 图片 pkl 第一维均一致。
- Weibo dataloader sanity 和小 batch forward 通过：`remote_panda_work/repro_logs/20260521_weibo_dataloader_forward_sanity.log`。
- Weibo-21 数据已上传到远端 `/root/autodl-tmp/panda_repro/panda/Weibo_21/`。
- Weibo-21 当前包含 `train_datasets.xlsx`、`val_datasets.xlsx`、`test_datasets.xlsx`、`nonrumor_images/`、`rumor_images/`。
- Weibo-21 图片命中率检查通过：train/val/test 缺图行数均为 0。
- Weibo-21 已生成 `train_loader.pkl`、`val_loader.pkl`、`test_loader.pkl`、`train_clip_loader.pkl`、`val_clip_loader.pkl`、`test_clip_loader.pkl`。
- Weibo-21 数据校验通过：train/val/test 行数分别为 4926/615/615，普通图片 pkl 与 CLIP 图片 pkl 第一维均一致。
- Weibo-21 图片预处理时发现 1 张截断图片 `bd4ef405gw1ey8wovbkpzj20hs0hst9p.jpg`，但 xlsx 样本未依赖它作为命中图片，不影响当前 split 校验。
- Weibo-21 dataloader sanity 通过：train/val/test batch 张量形状正常，图像 tensor finite。
- Weibo-21 小 batch forward 通过：主输出、text/image/fusion 辅助输出、`loss_rec` 均 finite，主输出非全常数。
- Gumbel/PANDA 随机性 sanity 通过：固定 seed 重复 forward 主输出 max diff 为 0；换 seed 后主输出和 neighbor selection 发生变化。
- 正式训练首次尝试在 epoch 1 验证时命中官方兼容性阻断：`roc_auc_score(...).round(4).tolist()` 对 Python float 不兼容。
- 已在远端打最小 metrics float code-compat patch：活动 `utils/utils.py::metrics` 中 `auc`、per-category precision/recall/fscore 改为 `round(float(...), 4)`；证据：`repro_logs/20260521_metrics_float_patch.diff`。
- Weibo-21 seed 42 paper-aligned 首跑已完成：batch size 32，lr 1e-4，epoch 50，early_stop 6，实际 early stop 于 epoch 25 后触发。
- Weibo-21 seed 42 最佳验证集出现在 epoch 19：Macro-F1 0.9560859504，Acc 0.9560975610，AUC 0.9874352195。
- Weibo-21 seed 42 最终测试结果：Macro-F1 0.9544656456，Acc 0.9544715447，AUC 0.9885563194。
- 已导出并独立重算 Weibo-21 seed 42 test 结果：`remote_panda_work/repro_logs/20260521_weibo21_seed42_test_metrics.json`，独立 AUC 0.9885986251，Macro-F1 0.9544656456，Acc 0.9544715447。
- 已导出 Weibo-21 seed 42 predictions：`remote_panda_work/repro_logs/20260521_weibo21_seed42_test_predictions.csv`，共 615 条预测。
- 首跑训练 stdout log 已同步：`remote_panda_work/logs/weibo21_panda_seed42_bs32_lr1e-4_rerun1.log`。
- Weibo-21 seed 2024 已完成：最佳验证集出现在 epoch 14，Macro-F1 0.9463051203，Acc 0.9463414634，AUC 0.9852141724。
- Weibo-21 seed 2024 最终测试结果：官方 log Macro-F1 0.9479607379，Acc 0.9479674797，AUC 0.9887149656；独立重算 AUC 0.9887466949，Macro-F1 0.9479607379，Acc 0.9479674797。
- Weibo-21 seed 2026 已完成：最佳验证集出现在 epoch 11，Macro-F1 0.9430888290，Acc 0.9430894309，AUC 0.9841882602。
- Weibo-21 seed 2026 最终测试结果：官方 log Macro-F1 0.9398272165，Acc 0.9398373984，AUC 0.9860602856；独立重算 AUC 0.9862506610，Macro-F1 0.9398272165，Acc 0.9398373984。
- Weibo-21 三 seed 独立重算汇总：
  - Macro-F1：0.9474178666 ± 0.0073342985 sample std。
  - Acc：0.9474254743 ± 0.0073321134 sample std。
  - AUC：0.9878653270 ± 0.0014003003 sample std。
- Weibo-21 三 seed 汇总已保存：`remote_panda_work/repro_logs/20260521_weibo21_three_seed_summary.json` 和 `remote_panda_work/repro_logs/20260521_weibo21_three_seed_summary.csv`。
- 已导出 Weibo-21 seed 2024/2026 predictions 和 metrics；本地证据位于 `remote_panda_work/repro_logs/`。
- Weibo seed 42 已完成：最佳验证集出现在 epoch 12，Macro-F1 0.9451457574，Acc 0.9454329775，AUC 0.9824354778。
- Weibo seed 42 最终测试结果：官方 log Macro-F1 0.9460606092，Acc 0.9460750853，AUC 0.9867426362；独立重算 AUC 0.9867687555，Macro-F1 0.9446950550，Acc 0.9447098976。
- Weibo seed 2024 已完成：最佳验证集出现在 epoch 15，Macro-F1 0.9381392671，Acc 0.9383155397，AUC 0.9826676330。
- Weibo seed 2024 最终测试结果：官方 log Macro-F1 0.9385662953，Acc 0.9385665529，AUC 0.9852575727；独立重算 AUC 0.9854012283，Macro-F1 0.9378829171，Acc 0.9378839590。
- Weibo seed 2026 已完成：最佳验证集出现在 epoch 27，Macro-F1 0.9452906321，Acc 0.9454329775，AUC 0.9836981756。
- Weibo seed 2026 最终测试结果：官方 log Macro-F1 0.9426614481，Acc 0.9426621160，AUC 0.9874954291；独立重算 AUC 0.9874870337，Macro-F1 0.9419785490，Acc 0.9419795222。
- Weibo 三 seed 独立重算汇总：
  - Macro-F1：0.9415188403 ± 0.0034292571 sample std。
  - Acc：0.9415244596 ± 0.0034356471 sample std。
  - AUC：0.9865523392 ± 0.0010596098 sample std。
- Weibo 三 seed 汇总已保存：`remote_panda_work/repro_logs/20260521_weibo_three_seed_summary.json` 和 `remote_panda_work/repro_logs/20260521_weibo_three_seed_summary.csv`。
- 实验日志、metrics、predictions、summary 和状态文档已同步到 GitHub 日志仓库 `CmmmMMM407/PANDA-FUXIAN`；最新 commit 以仓库 `main` 分支为准。
- 已导出 Weibo seeds 42/2024/2026 predictions 和 metrics；本地证据位于 `remote_panda_work/repro_logs/`。
- 远端 checkpoint 已按 seed 备份：
  - `/root/autodl-tmp/panda_repro/panda/param_model/FTmodel/checkpoints_by_seed/weibo21_seed42_parameter_panda.pkl`
  - `/root/autodl-tmp/panda_repro/panda/param_model/FTmodel/checkpoints_by_seed/weibo21_seed2024_parameter_panda.pkl`
  - `/root/autodl-tmp/panda_repro/panda/param_model/FTmodel/checkpoints_by_seed/weibo21_seed2026_parameter_panda.pkl`
  - `/root/autodl-tmp/panda_repro/panda/param_model/FTmodel/checkpoints_by_seed/weibo_seed42_parameter_panda.pkl`
  - `/root/autodl-tmp/panda_repro/panda/param_model/FTmodel/checkpoints_by_seed/weibo_seed2024_parameter_panda.pkl`
  - `/root/autodl-tmp/panda_repro/panda/param_model/FTmodel/checkpoints_by_seed/weibo_seed2026_parameter_panda.pkl`

## 当前卡点

1. Weibo-21 与 Weibo 三 seed 均值均略低于 PANDA 论文报告的 F1/Acc，但 AUC 基本对齐；最终报告需要解释 seed 波动、官方代码兼容补丁和复现边界。
2. 当前使用了必要 code-compat patch，最终报告必须清楚区分 official commit、compat patch 和非算法性修改。

## 下一步最高优先级

1. 整理 Weibo-21 与 Weibo 三 seed 主表。
2. 整理 code-compat patch 说明，避免把 diagnostic 或兼容性信息混入算法结论。
3. 与 PANDA 论文报告结果、MMDFND、DAMMFND 结果比较。
4. 写复现实验阶段复盘和最终复现报告。

## 当前推荐下一跑命令

```bash
mkdir -p param_model/FTmodel logs

python main.py \
  --dataset weibo21 \
  --model_name FTmodel \
  --gpu 0 \
  --batchsize 32 \
  --lr 1e-4 \
  --epoch 50 \
  --seed 42 \
  --early_stop 6
```

当前不建议继续启动新训练，优先完成日志同步和结果写作。

## 本文件维护规则

- 只保留当前最重要状态，不写长篇流水账。
- 每次实验后更新当前卡点和下一步。
- 详细过程写入 `experiment_log.md`。
- 每次实验后将新增日志、metrics、predictions、summary 和状态文档同步到 GitHub 日志仓库 `https://github.com/CmmmMMM407/PANDA-FUXIAN`。
- 同步前确认不包含服务器密码、token、私钥、完整连接凭据、checkpoint、权重或原始数据集。
