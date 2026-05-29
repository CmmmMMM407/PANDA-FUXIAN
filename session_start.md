# 新会话启动清单

最后整理：2026-05-30  
完整旧版快照：`docs/archive/full_snapshots_20260528/root/session_start.md`

## 必读顺序

每次重新接手本项目，先读：

1. `current_status.md`
2. `todo.md`
3. `project_overview.md`
4. `docs/PANDA_SOTA冲刺与论文实验总方案.md`
5. `experiment_log.md` 最近几条
6. `docs/README.md`
7. `docs/archive/README.md`

需要追历史方法细节时再读：

- `docs/archive/method_rounds/创新方案赛马总控与实施协议.md`
- `docs/archive/method_rounds/创新方法验证深度复审.md`
- `docs/archive/method_rounds/PANDA源码第一性原理审计与Round6方案升级.md`
- `docs/archive/registries/round6_candidate_registry.md`
- `docs/archive/method_rounds/新创新方案_Round7PANDA_RiskAwareFinalBoundary.md`
- `docs/archive/registries/round7_candidate_registry.md`

## 代码读取规则

PANDA 活代码不在本地项目文件夹。本地 `remote_panda_work/` 只是远端日志、代码片段和实验结果的证据副本。读取源码、确认实现、查看最新 diff 或修改代码时，必须先登录远端：

```bash
ssh panda-autodl
cd /root/autodl-tmp/panda_repro/panda
```

后续判断以该远端仓库为准。

## 当前默认路线

1. PANDA、MMDFND、DAMMFND 的 Weibo-21 / Weibo reproduced baselines 已完成；主表使用 reproduced baseline。
2. 当前没有 `Primary-Candidate`，不直接启动两数据集三 seed test 主表；Round12-R15 当前作用域已按门控闭环，Round15 final freeze/test 未解锁。
3. CS-PANDA、clean Reliability-aware selector、uncertainty stable-source、R3、历史 R4、P0/P1、Round 2、Round 3、Round 4、Round 5、Round 6 当前作用域均已验证或归档。
4. Round 7 已完成 D2/D3、D3.5、R7-A/R7-D D4-lite。R7-A 只保留 `D4-lite Feasible-B trend`；R7-D current sample aux 被 static aux 2.0 打穿；R7-B/R7-C 只保留 path evidence。
5. Round 8、Round 9、Round 10、Round 11 当前作用域均已闭环：R8-B static aux 2.0 有训练动力学正信号但 D5 不稳定；Round9 CUE/DGL-Aux No-Go；Round10 BUA D2.5 显示 utility allocation 干净但 boundary gate 不成立；Round11 UEA D4 消融显示 current utility-entropy aux allocation 未打过 static aux 2.0，且 reverse-utility control 追平 best control。
6. Round12-R15 当前作用域已闭环：Round12 ensemble diagnostic-only no-go to Round15；Round13 ADWA D3.5 feasible 但 D4 no-go to D5；Round14 launch gate no-go to B/C-current-assets；Round15 未启动。
7. Round12 的关键信号是 oracle any-correct 空间大但 learned/simple ensemble 提升不稳；Round13 的关键信号是 ADWA 梯度可行但被 static aux 2.0、generic DWA 和 deterministic/same-budget/detached controls 打穿；Round14 的关键限制是没有 split-safe OOF utility target。
8. 当前没有 `Primary-Candidate`，不直接启动两数据集三 seed test 主表。
9. 三 seed val 通过并冻结最终 primary config 前，不导出、不打开、不分析 test。

## 验证深度规则

- `D0/D1`：只能写 Evidence-only / Blocked / Provisional，不能 No-Go。
- `D2/D3`：只否定当前 direct probe、offline/frozen/proxy 变体。
- `D3.5/D4-lite`：只提供梯度可达性和短训趋势。
- `D4`：可判当前训练实现是否值得复核。
- `D5`：可支持稳定性和 `Primary-Candidate` 排名。

## 必守事项

- 所有 PANDA 运行显式 `--model_name FTmodel`。
- 短训默认 batch size 32、lr `1e-4`、epoch 5、early stop 6；正式 paper-aligned 训练再恢复 epoch 50。
- 每个新候选必须先有 manifest，并记录 `allowed_splits=["train","val"]`、`test_split_exported=false`、`test_used_for_decision=false`。
- 每次实验结束后更新 `current_status.md`、`todo.md`、`experiment_log.md`。
- 同步 GitHub 前排除服务器密码、token、私钥、完整 SSH 连接串、checkpoint、权重、原始数据、大 `.npz`、压缩包和含样本正文的预测长表。
