# TODO

## P0：立即要做

- [x] 在 AutoDL 租用 RTX 4090 机器。
- [x] 选择 Python 3.10 + PyTorch 2.1.x + CUDA 12.1 镜像。
- [x] 克隆 PANDA 官方仓库：https://github.com/lu-wayne/panda
- [x] 克隆实验日志仓库：https://github.com/CmmmMMM407/PANDA-FUXIAN
- [x] 创建 conda 环境并安装 PANDA / MMDFND 依赖。
- [x] 记录环境：`nvidia-smi`、`python --version`、`torch.__version__`、`pip freeze`。
- [x] 记录 PANDA 官方 commit，并确认是否为 `03e4c003e83480fe94ac52120522b34e4224f17b` 或更新版本。

## P0：数据与权重准备

- [x] 准备 Weibo-21 数据。
- [x] 检查 `train_datasets.xlsx`、`val_datasets.xlsx`、`test_datasets.xlsx` 是否存在。
- [x] 检查 Weibo-21 图片目录：`nonrumor_images/`、`rumor_images/`。
- [x] 准备 `pretrained_model/chinese_roberta_wwm_base_ext_pytorch/`。
- [x] 准备 `mae_pretrain_vit_base.pth`。
- [x] 准备或确认 CN-CLIP ViT-B-16 权重，并记录 `load_from_name("ViT-B-16", download_root="./")` 的实际缓存文件和 hash。
- [x] 运行 Weibo-21 图片 pkl 预处理，生成 `train_loader.pkl`、`val_loader.pkl`、`test_loader.pkl`。
- [x] 运行 Weibo-21 CN-CLIP 图片 pkl 预处理，生成 `train_clip_loader.pkl`、`val_clip_loader.pkl`、`test_clip_loader.pkl`。
- [x] 校验 xlsx 行数、普通图片 pkl 长度、CLIP 图片 pkl 长度三者一致。

## P0：sanity gate

- [x] 跑 import smoke test。
- [x] 跑数据 manifest：样本数、label 分布、category 分布、图片命中率。
- [x] 跑权重 manifest：文件大小、hash、关键 tensor 非零检查。
- [x] 跑 MAE checkpoint sanity：确认 `mae_pretrain_vit_base.pth` 含 `model` key，关键 tensor 非零。
- [x] 跑 CN-CLIP 图像 sanity：真实图、blank 图、noise 图 embedding 应不同。
- [x] 跑 PANDA 代码路径 sanity：确认 `--model_name FTmodel` 调用的是 `model/PANDA.py`。
- [x] 跑 PANDA 构造函数 sanity：确认不会被 `dataset_type` 参数或共享专家列表初始化问题阻断。
- [x] 若必须打 code-compat patch，保存错误栈、`git diff`、补丁目的和重新运行结果。
- [x] 跑小 batch forward：输出 finite，非 NaN，不全常数。
- [x] 跑 Gumbel/PANDA 随机性 sanity：固定随机种子或固定 neighbor selection 后再做重复 forward 对比。

## P1：正式复现实验

- [x] Weibo-21 seed 42，paper-aligned 参数首跑。
- [x] 保存 stdout log、metrics.json、predictions.csv、checkpoint。
- [x] 独立重算 macro-F1、Acc、AUC。
- [x] 若结果合理，补 Weibo-21 seeds 2024 和 2026。
- [x] 迁移到 Weibo，重复数据 gate 与训练。

## P2：分析与写作

- [x] 汇总 Weibo-21 三 seed 均值和标准差。
- [x] 汇总 Weibo 三 seed 均值和标准差。
- [ ] 与 MMDFND、DAMMFND、PANDA 论文报告结果比较。
- [ ] 写复现实验阶段复盘。
- [ ] 整理最终复现报告。

## 每次会话结束前固定动作

- [x] 更新 `current_status.md`。
- [x] 追加 `experiment_log.md`。
- [x] 刷新本文件的 TODO 状态。
- [ ] 将新增实验日志、metrics、predictions、summary 和状态文档同步到 GitHub 日志仓库 `CmmmMMM407/PANDA-FUXIAN`。
- [ ] 同步前检查不包含 checkpoint、权重、原始数据集、服务器密码、token、私钥或完整连接凭据。
- [ ] 若读了新论文或仓库，更新 `reading_notes.md`。
- [ ] 不在任何项目文件中写入服务器密码、token、私钥或完整 SSH 凭据。
