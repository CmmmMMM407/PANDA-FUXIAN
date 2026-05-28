# Weibo-21 seed42 5-epoch training-control sanity

This is a val-only sanity gate for method direction. Test metrics were exported because the training script evaluates test after best-val checkpoint loading, but route decisions below use validation evidence only.

## Key validation ranking

- deterministic_l0: Macro-F1 0.939835, Acc 0.939837, AUC 0.981206, ECE 0.023748, Brier 0.049289, weak-domain F1 0.896274, neighbor changes vs deterministic 0/615
- branch_fusion_clip_l1.0: Macro-F1 0.939797, Acc 0.939837, AUC 0.980381, ECE 0.023782, Brier 0.050389, weak-domain F1 0.922269, neighbor changes vs deterministic 231/615
- branch_fusion_l0.05: Macro-F1 0.933331, Acc 0.933333, AUC 0.983691, ECE 0.017475, Brier 0.047983, weak-domain F1 0.886914, neighbor changes vs deterministic 17/615
- branch_l1.0: Macro-F1 0.931698, Acc 0.931707, AUC 0.977800, ECE 0.024408, Brier 0.054445, weak-domain F1 0.922269, neighbor changes vs deterministic 373/615
- clip_l1.0: Macro-F1 0.931655, Acc 0.931707, AUC 0.980550, ECE 0.018454, Brier 0.049410, weak-domain F1 0.896521, neighbor changes vs deterministic 174/615
- branch_fusion_l1.0: Macro-F1 0.930081, Acc 0.930081, AUC 0.980920, ECE 0.027924, Brier 0.051067, weak-domain F1 0.887521, neighbor changes vs deterministic 365/615
- random_l1.0: Macro-F1 0.930063, Acc 0.930081, AUC 0.978614, ECE 0.017006, Brier 0.055448, weak-domain F1 0.922269, neighbor changes vs deterministic 362/615
- fusion_l1.0: Macro-F1 0.929936, Acc 0.930081, AUC 0.980011, ECE 0.029195, Brier 0.056689, weak-domain F1 0.870449, neighbor changes vs deterministic 142/615
- confidence_uncertainty_l1.0: Macro-F1 0.926822, Acc 0.926829, AUC 0.979778, ECE 0.027443, Brier 0.057040, weak-domain F1 0.887252, neighbor changes vs deterministic 350/615
- overconfidence_l1.0: Macro-F1 0.926822, Acc 0.926829, AUC 0.979778, ECE 0.027443, Brier 0.057040, weak-domain F1 0.887252, neighbor changes vs deterministic 350/615
- panda_gumbel_l0: Macro-F1 0.917073, Acc 0.917073, AUC 0.976393, ECE 0.031822, Brier 0.060953, weak-domain F1 0.887856, neighbor changes vs deterministic 542/615

## Go/no-go interpretation

- No-Go for current immediate two-dataset three-seed reliability-aware selector implementation: no reliability/disagreement variant beats deterministic eval on validation Macro-F1/Acc. This does not exclude reliability/calibration diagnostics or a substantially different training-time mechanism.
- Conditional signal: branch_fusion_clip is essentially tied with deterministic on val Macro-F1 but uses CLIP and does not provide a clean branch/fusion-only mechanism; branch_fusion l0.05/l1.0 and branch/fusion-only trail deterministic.
- Random and confidence/overconfidence controls do not explain the deterministic improvement, but confidence_uncertainty and overconfidence are mathematically equivalent under the current absolute-distance-to-domain-mean selector, so overconfidence is not an independent control in this implementation.
- Main implementation insight: current train-time reliability stats are online per epoch and the selector uses abs(score - domain_mean); next method iteration should test deterministic/stability regularization and an EMA or pre-epoch domain reliability prototype, plus signed reliability penalties if overconfidence is meant to be a distinct control.
