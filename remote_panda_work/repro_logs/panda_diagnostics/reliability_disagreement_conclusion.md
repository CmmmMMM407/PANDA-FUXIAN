# Reliability-aware Disagreement Conclusion

- weibo: CLIP-only val error AUC=0.5087, full conflict val error AUC=0.7463, confidence-uncertainty val error AUC=0.8589; selected offline lambda=0, high-low Jaccard gap=0.0000.
- weibo21: CLIP-only val error AUC=0.5314, full conflict val error AUC=0.8515, confidence-uncertainty val error AUC=0.8768; selected offline lambda=0.05, high-low Jaccard gap=0.0245.

当前 gate 不支持把方法强写成“图文冲突因果驱动”的结论：CLIP-only 信号在验证集上接近随机，而 full conflict 的主要增益来自 branch disagreement / fusion uncertainty / confidence-uncertainty 一类可靠性信号。因此更稳妥的论文叙事应改为 reliability-aware multimodal disagreement selection：把多模态分支分歧与融合不确定性作为邻域迁移可靠性的诊断与调制信号，并用 deterministic/offline selector 行为分析证明它是否真正改变 neighbor-domain selection；Weibo-21 可作为机制重点，Weibo 目前只能作为无明显 re-ranking 收益的负例或边界条件。
