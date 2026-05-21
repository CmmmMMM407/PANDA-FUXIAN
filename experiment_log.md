# 实验日志

本文件按日期记录实验与决策。每条记录只写：目标、操作、参数、结果、结论、下一步。

## 2026-05-21：确定复现对象与可复现 baseline

目标：

- 为中文多模态假新闻检测选择最新且可复现的 baseline。

操作：

- 调研 Weibo / Weibo-21 上的近期方法。
- 比较 RAMM、PANDA、DAMMFND、MMDFND。

结果：

- RAMM 报告结果最强，但论文给出的 GitHub 链接目前 404，暂不可复现。
- PANDA 有官方代码仓库，且在 Weibo 和 Weibo-21 上报告了较强结果。
- DAMMFND 和 MMDFND 可作为可复现 baseline。

结论：

- 本项目主复现方法选择 PANDA。
- 当前可复现实验主线为：MMDFND / DAMMFND / PANDA。
- RAMM 只作为 related work 或 reported SOTA 参考，不放入正式复现实验主表。

下一步：

- 准备 PANDA 复现环境和数据。

## 2026-05-21：核对 PANDA 官方环境要求

目标：

- 确认 AutoDL 上租用云算力时应选择什么环境。

操作：

- 阅读 PANDA README 和 requirements。
- 对照 MMDFND README 和 requirements。
- 检查 PANDA 代码中的关键依赖：BERT、MAE、CN-CLIP、openprompt、pandas、numpy。

参数/环境建议：

```bash
RTX 4090 24GB
Ubuntu 20.04 / 22.04
Python 3.10
PyTorch 2.0 - 2.2
CUDA 11.8 或 12.1
```

结果：

- PANDA 官方没有固定 PyTorch 版本，但固定了若干旧依赖。
- `pandas==1.4.2`、`numpy==1.23.2`、`openprompt==1.0.1` 更适合 Python 3.10。

结论：

- 推荐 AutoDL 镜像：PyTorch 2.1.x + CUDA 12.1 + Python 3.10。
- 避免 Python 3.11/3.12。

下一步：

- 在 AutoDL 创建环境后，先跑 import smoke test。

## 2026-05-21：发现 PANDA 官方代码关键默认值问题

目标：

- 确认 PANDA 官方仓库的实际运行入口。

操作：

- 阅读 `main.py`、`run.py` 和 `model/PANDA.py`。

结果：

- `main.py` 默认 `--model_name clean_vib`。
- `run.py` 中 `model_name == FTmodel` 时才调用 `model/PANDA.py` 的 Trainer。
- README 中的 `python main.py` 不足以保证跑的是 PANDA。

结论：

- 所有 PANDA 正式实验命令必须显式包含 `--model_name FTmodel`。
- 实验日志中必须记录模型分支和 checkpoint 文件名。

下一步：

- 在正式训练前增加代码路径 sanity check。

## 2026-05-21：建立跨会话同步文件

目标：

- 在项目文件夹中建立长期背景、当前状态、实验日志、文献笔记、待办事项和新会话启动模板。

操作：

- 创建以下文件：
  - `project_overview.md`
  - `current_status.md`
  - `experiment_log.md`
  - `reading_notes.md`
  - `todo.md`
  - `session_start.md`

结果：

- 项目上下文从聊天记录迁移到标准化文件。

结论：

- 后续新会话只需要先读取 `project_overview.md`、`current_status.md`、`todo.md` 和 `experiment_log.md` 最近几条即可接上项目。

下一步：

- 在 AutoDL 实际配置环境后，把安装结果追加到本文件。

## 2026-05-21：根据 AstraNav-Memory 复盘审计 PANDA 复现文件夹

目标：

- 检查当前项目文件夹是否存在敏感信息、缺失文件、与 PANDA 官方代码不一致或过于乐观的复现假设。

操作：

- 读取 `/Users/cm/Documents/Astranav 论文/AstraNav-Memory实验复盘与经验教训.docx`。
- 拉取并核验 PANDA 官方仓库 main 分支。
- 本次核验官方 commit：`03e4c003e83480fe94ac52120522b34e4224f17b`。
- 对照 `README.MD`、`requirements.txt`、`main.py`、`run.py`、`model/PANDA.py`、Weibo-21 数据预处理脚本和 dataloader。

结果：

- 发现 `project_overview.md` 中有远程服务器密码和 SSH 信息，已移除。
- 发现 `session_start.md` 在日志中被记录为已创建，但本地缺失，已补建。
- 新增 `.gitignore`，避免 `.DS_Store`、数据、权重、checkpoint、pkl 和密钥类文件进入仓库。
- 新增 `official_code_audit.md`。
- 删除本地 `.DS_Store`。
- 给 `PANDA复现实验规划与日志规范.docx` 追加“2026-05-21 官方代码审计补充”，并通过 docx business validation。
- 发现官方当前代码除 `--model_name FTmodel` 外，还需要额外验证：`dataset_type` 参数兼容、共享专家列表初始化、`save_param_dir` 创建路径、Gumbel 随机性、逐样本预测导出。

结论：

- 当前规划方向正确，但必须把“能否实例化 PANDA 模型”提前为 P0 gate。
- 若 clean official commit 报错，允许最小 code-compat patch，但必须保存错误栈、`git diff` 和补丁说明。
- diagnostic patch 结果不得混入 official-aligned 主表。

下一步：

- 在 AutoDL 上完成环境后，先跑 import smoke test 和 `FTmodel` 构造函数 sanity，再准备完整训练。

## 2026-05-21：AutoDL 环境搭建、代码兼容补丁与权重 gate

目标：

- 按计划顺序在 AutoDL 云算力上启动 PANDA 复现，先完成环境、代码路径、构造函数和权重 sanity gate。

操作：

- 为远端配置本机 SSH 密钥别名 `panda-autodl`。
- 在远端 `/root/autodl-tmp/panda_repro/` clone PANDA、实验日志仓库和 MMDFND 参考仓库。
- 启用 AutoDL 学术加速：`source /etc/network_turbo`。
- 安装 PANDA requirements；`cn_clip` 通过 OFA-Sys/Chinese-CLIP 官方仓库安装为 `cn-clip==1.5.1`。
- 运行 PANDA import smoke test、`Trainer` 构造函数 sanity、mock 模型构造 sanity、真实权重模型构造 sanity。
- 下载 RoBERTa、MAE、CN-CLIP 权重并生成 hash manifest。

参数：

```bash
ssh panda-autodl
cd /root/autodl-tmp/panda_repro/panda
python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 1 --early_stop 1
```

结果：

- 远端 GPU：NVIDIA GeForce RTX 4090 24GB，driver 580.105.08。
- 远端环境：Python 3.10.8，PyTorch 2.1.2+cu118，CUDA 可用。
- PANDA commit：`03e4c003e83480fe94ac52120522b34e4224f17b`。
- MMDFND commit：`a8a79b776845fc684d0269f5341235c0b1ea5c02`。
- clean commit 命中官方阻断：`Trainer.__init__() got an unexpected keyword argument 'dataset_type'`。
- 已打最小 code-compat patch：接收 `dataset_type`、修复共享专家列表 append、修复 `save_param_dir` 被 `os.makedirs()` 写成 `None`。
- patch diff 保存在远端：`repro_logs/20260521_code_compat_patch.diff`。
- mock 构造通过；真实权重构造通过；PANDA 参数量为 514,266,705。
- 权重 manifest 保存在远端：`repro_logs/20260521_weight_manifest.txt`。
- MAE checkpoint 含 `model` key，150 个 tensor，关键 tensor 非零。
- CN-CLIP blank/noise embedding finite，L2 距离约 8.194。
- 官方入口当前停止在数据读取：缺少 `./Weibo_21/val_datasets.xlsx`。

结论：

- 当前代码和权重 gate 已通过，正式训练的唯一硬阻塞是 Weibo-21 数据尚未上传。
- 不能跳过数据 gate 直接训练；下一步必须先补齐 xlsx 和图片目录。

下一步：

- 上传或挂载 Weibo-21 到 `/root/autodl-tmp/panda_repro/panda/Weibo_21/`。
- 运行数据 manifest、图片命中率检查、普通图片 pkl 和 CN-CLIP 图片 pkl 预处理。
- 再跑小 batch forward 与 Gumbel 随机性 sanity。

## 2026-05-21：上传并配置 Weibo 与 Weibo-21 数据

目标：

- 将本地 Weibo 数据集 `data.zip` 和 Weibo-21 数据集 `weibo21分享/` 上传到 AutoDL，并放到 PANDA 代码实际读取的位置。

操作：

- 使用 `rsync --partial --progress` 上传以下文件到远端 `/root/autodl-tmp/panda_repro/incoming_data/`：
  - `/Users/cm/Downloads/data.zip`
  - `/Users/cm/Downloads/weibo21分享/nonrumor_images.zip`
  - `/Users/cm/Downloads/weibo21分享/rumor_images.zip`
  - `/Users/cm/Downloads/weibo21分享/train_datasets.xlsx`
  - `/Users/cm/Downloads/weibo21分享/val_datasets.xlsx`
  - `/Users/cm/Downloads/weibo21分享/test_datasets.xlsx`
- 在远端 `/root/autodl-tmp/panda_repro/panda/` 解压 `data.zip`，生成 `data/`。
- 建立软链接 `Weibo -> data`，对齐 `run.py` 中 `./Weibo/` 路径。
- 创建并填充 `/root/autodl-tmp/panda_repro/panda/Weibo_21/`。
- 解压 Weibo-21 图片 zip 到 `Weibo_21/nonrumor_images/` 和 `Weibo_21/rumor_images/`。
- 运行 Weibo-21 数据 manifest 和图片命中率检查。
- 用官方 `data_pre/weibo21_data_pre.py` 生成 `val_loader.pkl` 和 `test_loader.pkl`。
- 官方脚本生成 `train_loader.pkl` 时因 tensor 构造路径过慢，停止该进程，改用一次性等价预处理脚本补齐 `train_loader.pkl` 和全部 `*_clip_loader.pkl`；未修改项目源码。

结果：

- Weibo 远端路径：`/root/autodl-tmp/panda_repro/panda/Weibo -> data`。
- Weibo 校验通过：train/val/test 行数分别为 5415/843/1465；`*_loader.pkl` 和 `*_clip_loader.pkl` 第一维均与 csv 行数一致。
- Weibo-21 远端路径：`/root/autodl-tmp/panda_repro/panda/Weibo_21/`。
- Weibo-21 xlsx 行数：train 4926，val 615，test 615。
- Weibo-21 label 分布：
  - train：1 为 2479，0 为 2447。
  - val：1 为 310，0 为 305。
  - test：1 为 310，0 为 305。
- Weibo-21 图片命中率：train/val/test 缺图行数均为 0。
- Weibo-21 已生成并校验：
  - `train_loader.pkl` / `train_clip_loader.pkl`：第一维 4926。
  - `val_loader.pkl` / `val_clip_loader.pkl`：第一维 615。
  - `test_loader.pkl` / `test_clip_loader.pkl`：第一维 615。
- 图片预处理时发现 1 张截断图片 `bd4ef405gw1ey8wovbkpzj20hs0hst9p.jpg`，但当前 xlsx 样本未依赖它作为命中图片，不影响 split 对齐。

结论：

- Weibo 与 Weibo-21 数据均已放到 PANDA 运行入口需要的位置。
- Weibo-21 已解除数据与 pkl 阻塞，可以进入 dataloader sanity、小 batch forward 和正式首跑。

下一步：

- 跑 Weibo-21 dataloader 构造 sanity。
- 跑小 batch forward 与 Gumbel/PANDA 随机性 sanity。
- 启动 Weibo-21 seed 42 paper-aligned 首跑。

## 2026-05-21：Weibo-21 sanity gate 与 seed 42 首跑

目标：

- 完成 Weibo-21 dataloader、小 batch forward、Gumbel/PANDA 随机性 sanity，并执行 seed 42 paper-aligned 首跑。

操作：

- 在远端 `/root/autodl-tmp/panda_repro/panda` 激活 conda base 环境运行 sanity 和训练。
- 跑 Weibo-21 train/val/test dataloader sanity，检查 xlsx 行数、label/category 分布、首个 batch 的 10 个 tensor 形状与 finite 状态。
- 跑 val 小 batch forward，检查 PANDA 主输出、text/image/fusion 辅助输出、`loss_rec` 均 finite，且主输出非全常数。
- 固定 seed 和切换 seed 对比 `_gumbel_neighbor_selector` 与重复 forward，确认随机性可控。
- 启动 Weibo-21 seed 42 正式训练；第一次训练在 epoch 1 验证阶段命中 `utils/utils.py::metrics` float 兼容性错误。
- 打最小 code-compat patch：将活动 `metrics` 中 `roc_auc_score`、per-category `precision_score`、`recall_score`、`f1_score` 的 `.round(4).tolist()` 改为 `round(float(...), 4)`。
- 重新启动 Weibo-21 seed 42 训练，训练自然 early stop，并导出 test predictions 和 metrics。
- 将关键远端日志同步到本地 `remote_panda_work/`。

参数：

```bash
python main.py \
  --dataset weibo21 \
  --model_name FTmodel \
  --gpu 0 \
  --batchsize 32 \
  --lr 1e-4 \
  --epoch 50 \
  --early_stop 6
```

结果：

- dataloader sanity 通过：
  - train/val/test 行数分别为 4926/615/615。
  - 首个 batch 形状为 `[B,197]` 文本 token、mask、label、category、两路 `[B,3,224,224]` 图像、`[B,52]` CLIP text，以及 prompt 相关 3 个 `[B,197]` tensor。
  - 图像和 mask tensor finite。
- 小 batch forward 通过：
  - 主输出范围约 0.4876 到 0.4963，finite，非全常数。
  - text/image/fusion 辅助输出和 `loss_rec` 均 finite。
- Gumbel/PANDA 随机性 sanity 通过：
  - 固定 seed 重复 forward 主输出 max abs diff 为 0。
  - 换 seed 后主输出 max abs diff 约 0.00119。
  - 固定 seed 的 neighbor indices 一致，换 seed 后至少部分 neighbor 变化。
- 第一次正式训练阻断：
  - 报错：`AttributeError: 'float' object has no attribute 'round'`。
  - 触发位置：`utils/utils.py::metrics`。
  - 补丁证据：远端和本地 `remote_panda_work/repro_logs/20260521_metrics_float_patch.diff`。
- seed 42 训练完成：
  - early stop 在 epoch 25 后触发。
  - 最佳验证集出现在 epoch 19：Macro-F1 0.9560859504，Acc 0.9560975610，AUC 0.9874352195。
  - 最终 test log：Macro-F1 0.9544656456，Acc 0.9544715447，AUC 0.9885563194。
- 独立重算 test：
  - support 615。
  - AUC 0.9885986251。
  - Macro-F1 0.9544656456。
  - Acc 0.9544715447。
  - confusion matrix labels `[0,1]`：`[[290, 15], [13, 297]]`。
- 本地证据文件：
  - `remote_panda_work/repro_logs/20260521_weibo21_dataloader_sanity.log`
  - `remote_panda_work/repro_logs/20260521_weibo21_forward_gumbel_sanity.log`
  - `remote_panda_work/logs/weibo21_panda_seed42_bs32_lr1e-4_rerun1.log`
  - `remote_panda_work/repro_logs/20260521_weibo21_seed42_test_metrics.json`
  - `remote_panda_work/repro_logs/20260521_weibo21_seed42_test_predictions.csv`

结论：

- Weibo-21 seed 42 已完成一轮可追溯复现，结果高于 paper-aligned baseline 的合理区间，需要通过 seeds 2024/2026 判断稳定性。
- 当前 patch 均为运行兼容性补丁，不改变 PANDA 算法路径；最终报告必须单列说明。
- PANDA eval 仍包含 Gumbel 随机性；导出的 predictions 文件在导出前固定 seed 42。

下一步：

- 补 Weibo-21 seeds 2024 和 2026。
- 汇总 Weibo-21 三 seed 均值和标准差。
- 迁移到 Weibo 数据集并重复 sanity、训练和预测导出。

## 2026-05-21：Weibo-21 seeds 2024/2026 补跑与三 seed 汇总

目标：

- 补齐 Weibo-21 paper-aligned seeds 2024 和 2026。
- 保存每个 seed 的 stdout log、checkpoint、predictions.csv、metrics.json，并汇总三 seed 均值/标准差。

操作：

- 在远端 `/root/autodl-tmp/panda_repro/panda` 继续使用官方 commit `03e4c003e83480fe94ac52120522b34e4224f17b` 加最小 code-compat patch。
- 先将 seed 42 checkpoint 备份到 `param_model/FTmodel/checkpoints_by_seed/weibo21_seed42_parameter_panda.pkl`，避免后续训练覆盖。
- 运行 Weibo-21 seed 2024 和 seed 2026，均使用 paper-aligned 参数。
- 每个 seed 训练完成后，将 `param_model/FTmodel/parameter_panda.pkl` 复制为 seed 专属 checkpoint。
- 固定对应 seed 重新前向导出 test predictions，并用 sklearn 独立重算 Macro-F1、Acc、AUC。
- 将远端日志和预测文件同步到本地 `remote_panda_work/`。

参数：

```bash
python main.py \
  --dataset weibo21 \
  --model_name FTmodel \
  --gpu 0 \
  --batchsize 32 \
  --lr 1e-4 \
  --epoch 50 \
  --seed 2024 \
  --early_stop 6

python main.py \
  --dataset weibo21 \
  --model_name FTmodel \
  --gpu 0 \
  --batchsize 32 \
  --lr 1e-4 \
  --epoch 50 \
  --seed 2026 \
  --early_stop 6
```

结果：

- seed 2024：
  - 最佳验证集出现在 epoch 14：Macro-F1 0.9463051203，Acc 0.9463414634，AUC 0.9852141724。
  - 官方最终 test：Macro-F1 0.9479607379，Acc 0.9479674797，AUC 0.9887149656。
  - 独立重算 test：Macro-F1 0.9479607379，Acc 0.9479674797，AUC 0.9887466949。
  - confusion matrix labels `[0,1]`：`[[288, 17], [15, 295]]`。
- seed 2026：
  - 最佳验证集出现在 epoch 11：Macro-F1 0.9430888290，Acc 0.9430894309，AUC 0.9841882602。
  - 官方最终 test：Macro-F1 0.9398272165，Acc 0.9398373984，AUC 0.9860602856。
  - 独立重算 test：Macro-F1 0.9398272165，Acc 0.9398373984，AUC 0.9862506610。
  - confusion matrix labels `[0,1]`：`[[293, 12], [25, 285]]`。
- Weibo-21 三 seed 独立重算汇总：
  - Macro-F1：0.9474178666 ± 0.0073342985 sample std。
  - Acc：0.9474254743 ± 0.0073321134 sample std。
  - AUC：0.9878653270 ± 0.0014003003 sample std。
- 本地证据文件：
  - `remote_panda_work/logs/weibo21_panda_seed2024_bs32_lr1e-4.log`
  - `remote_panda_work/logs/weibo21_panda_seed2026_bs32_lr1e-4.log`
  - `remote_panda_work/repro_logs/20260521_weibo21_seed2024_test_metrics.json`
  - `remote_panda_work/repro_logs/20260521_weibo21_seed2024_test_predictions.csv`
  - `remote_panda_work/repro_logs/20260521_weibo21_seed2026_test_metrics.json`
  - `remote_panda_work/repro_logs/20260521_weibo21_seed2026_test_predictions.csv`
  - `remote_panda_work/repro_logs/20260521_weibo21_three_seed_summary.json`
  - `remote_panda_work/repro_logs/20260521_weibo21_three_seed_summary.csv`
- 远端 checkpoint：
  - `param_model/FTmodel/checkpoints_by_seed/weibo21_seed42_parameter_panda.pkl`
  - `param_model/FTmodel/checkpoints_by_seed/weibo21_seed2024_parameter_panda.pkl`
  - `param_model/FTmodel/checkpoints_by_seed/weibo21_seed2026_parameter_panda.pkl`

结论：

- Weibo-21 三 seed AUC 与论文报告 0.988 基本对齐，但 Macro-F1/Acc 三 seed 均值约 0.9474，低于论文报告 F1 0.958 / Acc 0.959。
- seed 间存在可见波动：seed 42 最高，seed 2026 最低，因此后续报告必须使用多 seed 均值/标准差而不是单次最好值。
- 当前结果仍属于 paper-aligned + code-compat patch 复现，不应和 diagnostic patch 结果混表。

下一步：

- 迁移到 Weibo 数据集，重复 dataloader sanity、小 batch forward、正式训练、预测导出和三 seed 汇总。

## 2026-05-21：Weibo sanity gate、三 seed 训练与汇总

目标：

- 将 PANDA paper-aligned 复现实验迁移到 Weibo 数据集。
- 完成 Weibo dataloader sanity、小 batch forward、seeds 42/2024/2026 正式训练、逐样本预测导出和三 seed 汇总。

操作：

- 在远端 `/root/autodl-tmp/panda_repro/panda` 运行 Weibo dataloader sanity，确认 train/val/test 行数、label/category 分布、batch 张量形状和图像 finite。
- 运行 Weibo 小 batch forward，确认主输出、text/image/fusion 辅助输出和 `loss_rec` 均 finite。
- 依次运行 Weibo seeds 42、2024、2026 的 paper-aligned 训练。
- 每个 seed 训练完成后备份 checkpoint，导出 test predictions，并用 sklearn 独立重算 Macro-F1、Acc、AUC。
- 生成 Weibo 三 seed summary，并同步本地 `remote_panda_work/`。

参数：

```bash
python main.py \
  --dataset weibo \
  --model_name FTmodel \
  --gpu 0 \
  --batchsize 32 \
  --lr 1e-4 \
  --epoch 50 \
  --early_stop 6 \
  --seed {42,2024,2026}
```

结果：

- Weibo dataloader sanity 通过：
  - train/val/test 行数分别为 5415/843/1465。
  - 首个 batch 形状为 `[B,197]` 文本 token、mask、label、category、两路 `[B,3,224,224]` 图像、`[B,52]` CLIP text，以及 prompt 相关 3 个 `[B,197]` tensor。
  - 图像和 CLIP 图像 tensor finite。
- Weibo 小 batch forward 通过：
  - 主输出范围约 0.4992 到 0.5078，finite，非全常数。
  - text/image/fusion 辅助输出和 `loss_rec` 均 finite。
- seed 42：
  - 最佳验证集出现在 epoch 12：Macro-F1 0.9451457574，Acc 0.9454329775，AUC 0.9824354778。
  - 官方最终 test：Macro-F1 0.9460606092，Acc 0.9460750853，AUC 0.9867426362。
  - 独立重算 test：Macro-F1 0.9446950550，Acc 0.9447098976，AUC 0.9867687555。
  - confusion matrix labels `[0,1]`：`[[680, 29], [52, 704]]`。
- seed 2024：
  - 最佳验证集出现在 epoch 15：Macro-F1 0.9381392671，Acc 0.9383155397，AUC 0.9826676330。
  - 官方最终 test：Macro-F1 0.9385662953，Acc 0.9385665529，AUC 0.9852575727。
  - 独立重算 test：Macro-F1 0.9378829171，Acc 0.9378839590，AUC 0.9854012283。
  - confusion matrix labels `[0,1]`：`[[684, 25], [66, 690]]`。
- seed 2026：
  - 最佳验证集出现在 epoch 27：Macro-F1 0.9452906321，Acc 0.9454329775，AUC 0.9836981756。
  - 官方最终 test：Macro-F1 0.9426614481，Acc 0.9426621160，AUC 0.9874954291。
  - 独立重算 test：Macro-F1 0.9419785490，Acc 0.9419795222，AUC 0.9874870337。
  - confusion matrix labels `[0,1]`：`[[687, 22], [63, 693]]`。
- Weibo 三 seed 独立重算汇总：
  - Macro-F1：0.9415188403 ± 0.0034292571 sample std。
  - Acc：0.9415244596 ± 0.0034356471 sample std。
  - AUC：0.9865523392 ± 0.0010596098 sample std。
- 本地证据文件：
  - `remote_panda_work/repro_logs/20260521_weibo_dataloader_forward_sanity.log`
  - `remote_panda_work/logs/weibo_panda_seed42_bs32_lr1e-4.log`
  - `remote_panda_work/logs/weibo_panda_seed2024_bs32_lr1e-4.log`
  - `remote_panda_work/logs/weibo_panda_seed2026_bs32_lr1e-4.log`
  - `remote_panda_work/repro_logs/20260521_weibo_seed42_test_metrics.json`
  - `remote_panda_work/repro_logs/20260521_weibo_seed42_test_predictions.csv`
  - `remote_panda_work/repro_logs/20260521_weibo_seed2024_test_metrics.json`
  - `remote_panda_work/repro_logs/20260521_weibo_seed2024_test_predictions.csv`
  - `remote_panda_work/repro_logs/20260521_weibo_seed2026_test_metrics.json`
  - `remote_panda_work/repro_logs/20260521_weibo_seed2026_test_predictions.csv`
  - `remote_panda_work/repro_logs/20260521_weibo_three_seed_summary.json`
  - `remote_panda_work/repro_logs/20260521_weibo_three_seed_summary.csv`

结论：

- Weibo 三 seed AUC 0.9866 ± 0.0011 与 PANDA 论文报告 AUC 0.987 基本对齐。
- Weibo 三 seed Macro-F1/Acc 均值约 0.9415，低于论文报告 F1 0.951 / Acc 0.953。
- Weibo 和 Weibo-21 均表现为 AUC 对齐、F1/Acc 略低，后续报告需要围绕随机性、官方代码兼容补丁、数据预处理一致性和 checkpoint 选择进行解释。

下一步：

- 将本轮新增日志、metrics、predictions、summary 和状态文档同步到 GitHub 日志仓库。
- 整理 Weibo-21 与 Weibo 三 seed 主表，开始写阶段复盘。

## 新日志模板

````markdown
## YYYY-MM-DD：实验标题

目标：

- 

操作：

- 

参数：

```bash

```

结果：

- 

结论：

- 

下一步：

- 
````
