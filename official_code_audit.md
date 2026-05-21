# PANDA 官方代码审计记录

审计日期：2026-05-21

审计依据：

- AstraNav-Memory 实验复盘：官方配置对齐不等于实验链路正确，必须先做权重、数据、模态传导和端到端 sanity gate。
- PANDA 官方仓库：https://github.com/lu-wayne/panda
- 本次核验的官方 commit：`03e4c003e83480fe94ac52120522b34e4224f17b`

## 结论

当前项目文件夹的总体方向正确，但原先清单仍偏乐观：它已经注意到 `--model_name FTmodel`、数据/权重缺失、路径混乱和 checkpoint 保存目录问题，但还没有显式覆盖官方当前代码里可能直接阻断运行的构造函数兼容问题、共享专家列表初始化问题、Gumbel 随机性问题和敏感凭据治理。

## 已修正的问题

1. `project_overview.md` 中曾写入远程服务器密码和 SSH 信息，已移除并改为凭据管理规则。
2. `experiment_log.md` 曾记录已创建 `session_start.md`，但文件不存在；本次补建。
3. 新增 `.gitignore`，避免 `.DS_Store`、数据集、权重、checkpoint、pkl 和本地密钥类文件进入仓库。
4. `project_overview.md`、`current_status.md`、`todo.md`、`reading_notes.md` 已补充官方代码审计发现。

## 官方代码需要重点验证的点

1. `main.py` 默认 `--model_name clean_vib`，不是 PANDA；PANDA 必须显式使用 `--model_name FTmodel`。
2. `run.py` 的 `FTmodel` 分支才会调用 `model/PANDA.py`。
3. `run.py` 调用 PANDA `Trainer` 时传入 `dataset_type=self.dataset_type`，但当前 `model/PANDA.py` 的 `Trainer.__init__` 没有 `dataset_type` 参数，可能触发 `TypeError`。
4. `model/PANDA.py` 中共享专家列表在初始化前被使用，可能触发 `AttributeError`。
5. `Trainer.__init__` 中首次创建保存目录时会把 `self.save_param_dir` 设为 `None`，导致 `torch.save` 路径异常。
6. `model/PANDA.py` 固定加载 `./mae_pretrain_vit_base.pth`，需要确认 checkpoint 包含 `model` key。
7. CN-CLIP 通过 `load_from_name("ViT-B-16", device="cuda", download_root="./")` 加载，必须记录实际下载文件、缓存位置和 hash，不要只凭文件名假设。
8. Weibo-21 运行路径为 `./Weibo_21/`，预处理脚本生成 `train_loader.pkl`、`val_loader.pkl`、`test_loader.pkl` 以及对应 `*_clip_loader.pkl`。
9. Gumbel neighbor selector 在 forward 中有随机噪声；重复 forward sanity 需要固定随机源或做诊断性 deterministic selector。
10. 官方代码不会自动导出逐样本预测，必须额外保存 `predictions.csv` 并独立重算 Macro-F1、Accuracy、AUC。

## 推荐最小 code-compat patch 原则

- 只有在 clean official commit 的 sanity gate 复现报错后才打补丁。
- 每个补丁必须只解决运行阻断，不改变算法意图。
- 补丁前后都要保存 `git diff`、错误栈、补丁说明和重新运行结果。
- code-compat patch 可以进入正式复现前置说明；diagnostic patch 的结果不能混入 official-aligned 主表。

## 下一步

1. 在 AutoDL 上 clone 官方仓库后先记录 commit。
2. 跑 import smoke test。
3. 在不训练的情况下执行 `--model_name FTmodel` 代码路径/构造函数 sanity。
4. 若触发 `dataset_type` 或共享专家初始化错误，打最小兼容补丁并记录。
5. 再进入数据、权重、模态传导 gate。
