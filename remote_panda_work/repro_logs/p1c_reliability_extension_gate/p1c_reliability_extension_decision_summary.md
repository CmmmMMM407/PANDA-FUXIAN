# P1-C Reliability / Evidential Extension Gate

Decision: **No-Go** for primary-method training.

Decision basis: validation rows only. No new training was launched, and test rows were not used for method selection.

## Seed42 val gate

The only seed42 validation variant that passed the previous Go/No-Go rule was `reliability_confidence_uncertainty_stable_source_reward_pre_epoch_l0p2`.

| variant | Macro-F1 | Acc | AUC | ECE | Brier | HCE | Weak F1 | Pass |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| deterministic_eval_l0 | 0.939835 | 0.939837 | 0.981206 | 0.023748 | 0.049289 | 0.022764 | 0.896274 | False |
| confidence_uncertainty + stable_source_reward l0.2 | 0.941395 | 0.941463 | 0.984960 | 0.023196 | 0.048348 | 0.014634 | 0.939651 | True |

Seed42 looked promising: Macro-F1 +0.156pp, Acc +0.163pp, AUC +0.375pp, ECE -0.055pp, Brier -0.094pp, HCE -0.813pp, and weak-domain Macro-F1 +4.338pp.

## Three-seed val recheck

| metric | deterministic mean | candidate mean | delta |
| --- | ---: | ---: | ---: |
| Macro-F1 | 0.937093 | 0.936018 | -0.001075 |
| Accuracy | 0.937127 | 0.936043 | -0.001084 |
| AUC | 0.982824 | 0.984188 | 0.001364 |
| ECE | 0.024160 | 0.023511 | -0.000649 |
| Brier | 0.051087 | 0.049435 | -0.001652 |
| HCE | 0.020596 | 0.016802 | -0.003794 |
| Weak Macro-F1 | 0.922273 | 0.936715 | 0.014442 |

Pass count: `2/3`. Seed 2024 is the failure case: validation Macro-F1 delta `-0.006513` and Accuracy delta `-0.006504`.

## Interpretation

- Uncertainty/reliability remains a strong diagnostic signal: confidence-uncertainty predicts validation errors better than CLIP-only and random controls in the existing diagnostics.
- As a method, the current extension fails the primary criterion because three-seed validation Macro-F1/Accuracy are below deterministic selection.
- The support-metric gains are real but not sufficient: calibration, HCE, AUC, and weak-domain improvements can coexist with overall F1/Acc degradation.
- P1-C should be retained as diagnostic/calibration analysis and as a possible second-stage add-on only after a primary final-boundary mechanism is found.
