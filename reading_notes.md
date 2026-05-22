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
