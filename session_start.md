# 新会话启动清单

每次重新接手本项目，先按顺序读取：

1. `current_status.md`
2. `todo.md`
3. `project_overview.md`
4. `official_code_audit.md`
5. `experiment_log.md` 最近三条
6. `reading_notes.md`

## 当前默认路线

1. Weibo-21 和 Weibo 三 seed paper-aligned 复现已完成，先读取 `current_status.md` 中的汇总结果。
2. 下一阶段优先同步 GitHub 日志仓库，并整理 Weibo-21 / Weibo 三 seed 主表。
3. 暂不建议继续启动新训练；先写 code-compat patch 说明、阶段复盘和最终复现报告。
4. 若后续补实验，仍使用 `--model_name FTmodel`、batch size 32、lr 1e-4、epoch 50、early_stop 6，并先做 sanity gate。
5. 任何代码兼容补丁、参数变更、数据处理变更都必须写入 `experiment_log.md` 和 run 目录的 `notes.md`。
6. 每次实验结束后，必须将新增实验日志、metrics、predictions、summary 和状态文档同步到 GitHub 日志仓库 `https://github.com/CmmmMMM407/PANDA-FUXIAN`；同步前确认不包含服务器密码、token、私钥、完整连接凭据或大 checkpoint。

## 禁止事项

- 不在项目文件或公开日志仓库中写入服务器密码、token、私钥、完整连接凭据。
- 不把 diagnostic patch 的结果混入 official-aligned 主表。
- 不跳过数据、权重和模态传导 sanity gate 直接跑长训练。
- 不只引用官方 stdout 指标，必须保存逐样本 score 并独立重算指标。
- 不把 checkpoint、权重、原始数据集或敏感凭据 push 到 GitHub 日志仓库。
