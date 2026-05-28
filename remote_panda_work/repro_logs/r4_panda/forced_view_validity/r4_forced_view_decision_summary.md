# R4 forced-view validity decision

Status: No-Go for current D2 PAD-top2 forced-view validity / immediate-training permission

Data use: Weibo-21 seed42 train/val only; test was not exported or analyzed.

Key checks:
- Anchor direct verification max abs diff: train=0.0, val=0.0.
- Train PAD top2 CE=0.0002581242, bottom2 CE=0.0002466201, random mean CE=0.0002470063; preliminary pass=False.
- Val PAD top2 CE=0.1577833134, bottom2 CE=0.1581670837, random mean CE=0.1586489953; preliminary pass=True.
- Shuffled PAD top2 val CE=0.1568494840, which is lower than PAD top2 CE=0.1577833134.
- PAD top2 perturbation is nonzero but small: train JSD=2.56523752e-07, val JSD=1.423958924e-05.

Decision:
- Do not start current R4 seed42 training from this gate.
- Do not freeze `r4_gate_config.yaml`.
- Record this as a current forced-view failure boundary or at most weak feasibility signal: forced non-self source views exist, but PAD top2 is not cleanly better than random/bottom/shuffled controls.
- This does not permanently exclude a new non-self/source protocol; that would need a new manifest and D4 validation.

Interpretation:
- The final classifier is only weakly sensitive to source-domain prompt interventions in the reproduced checkpoint.
- The useful signal, where present on val, is not uniquely tied to PANDA PAD ranking because shuffled PAD top2 is stronger on CE.
- This supports the broader boundary-condition story: changing source views alone is not enough evidence that neighbor-domain knowledge is driving the decision boundary.
