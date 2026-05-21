# PANDA 复现项目总览

## 项目定位

本项目用于复现 PANDA：Prototype-driven Asymmetric Neighbor-Domain Adaptation for Fake News Detection。

当前研究方向是中文多模态假新闻检测，重点关注多领域场景下文本、图片和领域信息如何共同影响真假新闻分类结果。

## 研究题目

暂定题目：

PANDA 在中文多模态多领域假新闻检测任务上的复现与误差分析

可选扩展题目：

多领域中文多模态假新闻检测中的负迁移缓解方法复现与分析

## 核心任务定义

输入：

- 新闻文本
- 新闻图片
- 新闻所属领域/domain

输出：

- 二分类标签：真实新闻或虚假新闻
- 预测概率或 score

目标：

- 复现 PANDA 在 Weibo-21 和 Weibo 上的主表结果
- 验证 PANDA 相比 MMDFND、DAMMFND 等 baseline 的提升是否可复现
- 记录复现过程中的环境、数据、权重、代码路径和指标差异

## 方法与基线

主方法：

- PANDA，全称 Prototype-driven Asymmetric Neighbor-Domain Adaptation
- 论文标题：From Blind Transfer to Wise Selection: Prototype-Driven Neighbor-Domain Adaptation for Fake News Detection
- 官方代码：https://github.com/lu-wayne/panda

可复现 baseline：

- MMDFND
- DAMMFND
- PANDA

仅作为 reported SOTA 参考：

- RAMM。论文报告结果较强，但公开 GitHub 链接目前不可访问，因此不作为可复现实验主表 baseline。

## 数据集

第一优先级：

- Weibo-21
- 中文、多模态、多领域假新闻检测数据集
- PANDA 论文主表目标：F1 0.958，Acc 0.959，AUC 0.988

第二优先级：

- Weibo
- 中文、多模态假新闻检测数据集，PANDA / MMDFND / DAMMFND 使用带领域标签版本
- PANDA 论文主表目标：F1 0.951，Acc 0.953，AUC 0.987

暂缓：

- FineFake
- 英文多模态多领域数据集；除非后续需要英文补充实验，否则第一阶段不跑

## 评价指标

主指标：

- Macro-F1
- Accuracy
- AUC

辅助记录：

- per-domain F1 / Acc / AUC
- real/fake precision、recall、F1
- prediction score
- sample id、label、pred、category、image id

## 默认实验环境

默认算力：

- AutoDL
- 单张 RTX 4090 24GB

推荐镜像：

- Ubuntu 20.04 或 22.04
- Python 3.10
- PyTorch 2.0 - 2.2
- CUDA 11.8 或 12.1

推荐首选：

```bash
PyTorch 2.1.x + CUDA 12.1 + Python 3.10
```

关键依赖：

```bash
transformers==4.31.0
transformers-stream-generator==0.0.4
numpy==1.23.2
pandas==1.4.2
openprompt==1.0.1
cn_clip
ftfy
regex
tqdm
scikit-learn
positional_encodings
openpyxl
git+https://github.com/openai/CLIP.git
```

## 约束条件

- 使用单张 RTX 4090 复现，不做多卡假设。
- 第一阶段只做中文数据集 Weibo-21 和 Weibo。
- 优先使用官方代码，不做未记录的代码修改。
- 所有代码修改、参数变化、数据处理变化必须写入 experiment_log.md 或 current_status.md。
- 不把 diagnostic patch 结果混入 official-aligned 结果。

## 官方代码关键坑

以下信息基于 2026-05-21 对 PANDA 官方仓库 main 分支的核验，当前 commit 为 `03e4c003e83480fe94ac52120522b34e4224f17b`。

1. PANDA README 写 `python main.py`，但 `main.py` 默认 `--model_name clean_vib`。
2. 真正调用 `model/PANDA.py` 的分支是 `--model_name FTmodel`。
3. 论文参数与代码默认值不完全一致：论文使用 batch size 32、lr 1e-4；代码默认 batch size 64、lr 1e-3。
4. 数据和预训练权重没有随 PANDA 仓库完整提供，需要沿用 MMDFND 的准备方式。
5. `run.py` 会把 Weibo-21 主数据路径设为 `./Weibo_21/`，但部分工具/历史脚本仍引用 `data/`、`./Weibo/` 或预处理 pkl 路径，必须在 manifest 里记录实际目录与软链接。
6. `run.py` 调用 `model/PANDA.py` 的 `Trainer` 时传入 `dataset_type=`，而当前 `Trainer.__init__` 签名没有该参数；正式训练前必须做构造函数 sanity，若确认报错，只能做最小兼容补丁并标为 code-compat patch。
7. 当前 `model/PANDA.py` 中 `self.text_share_expert`、`self.image_share_expert`、`self.fusion_share_expert`、`self.final_share_expert` 在初始化前被 `.append()` 使用，可能导致模型实例化阶段直接失败；必须在代码路径 gate 中验证。
8. `Trainer.__init__` 中 `self.save_param_dir = os.makedirs(save_param_dir)` 会在首次创建目录时把路径写成 `None`；训练前建议手动创建 `param_model/FTmodel`，或做最小补丁并记录。
9. PANDA 的 Gumbel neighbor selector 在 forward 中使用随机噪声，eval 模式下重复 forward 不一定 bitwise 一致；模态传导 gate 应固定随机种子或临时记录/固定 neighbor selection 后再判断。
10. 官方训练日志只打印指标并保存 `parameter_panda.pkl`，不会自动保存 `metrics.json` 和 `predictions.csv`；正式复现必须额外导出原始 score 并独立重算指标。

## 默认首跑命令

```bash
mkdir -p param_model/FTmodel logs

python main.py \
  --dataset weibo21 \
  --model_name FTmodel \
  --gpu 0 \
  --batchsize 32 \
  --lr 1e-4 \
  --epoch 50 \
  --early_stop 6 2>&1 | tee logs/weibo21_panda_seed42_bs32_lr1e-4.log
```

## 日志仓库

实验日志仓库：

https://github.com/CmmmMMM407/PANDA-FUXIAN

所有重要实验日志、环境记录、数据 manifest、权重 manifest、失败原因、metrics、predictions、summary 和阶段复盘都必须同步到该仓库。

每次实验结束固定执行：

- 将新增 stdout log、`metrics.json`、`predictions.csv`、summary 文件和状态文档同步到 GitHub 日志仓库。
- 同步前检查 `.gitignore` 和 `git status`，确认不会提交 checkpoint、权重、原始数据集、服务器密码、token、私钥或完整连接凭据。
- 对大文件只记录远端路径、大小、hash 和用途，不把文件本体 push 到 GitHub。

远程服务器账号、密码、端口、token、私钥等凭据不得写入本项目文件或公开日志仓库。、AutoDL 控制台、SSH config 或未提交的私密笔记。

远程连接已配置为本机 SSH 密钥别名：

```bash
ssh panda-autodl
```

远程服务器账号、密码、端口、token、私钥等凭据不得写入本项目文件或公开日志仓库。
下载东西尽量从清华源下载，如果是国外资源可以使用 autodl 官方的学术资源加速指令



## 工作原则

本项目继承 AstraNav-Memory 复盘中的核心经验：

- 官方配置对齐不等于实验链路正确。
- 先做数据、权重、模态传导 sanity gate，再跑完整实验。
- 反事实探针要尽早做。
- 日志字段要面向排错，而不是只记录最终分数。
- 每轮实验结束都要沉淀到 current_status.md、experiment_log.md 和 todo.md。
