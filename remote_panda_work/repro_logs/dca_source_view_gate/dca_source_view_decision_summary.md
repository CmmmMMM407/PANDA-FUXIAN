# P0-B DCA/source-view sensitivity decision

Status: No-Go for current D2 late DCA/source-view frozen probe

Data use: Weibo-21 seed42 train/val only; test was not exported or analyzed.

Key checks:
- Anchor direct verification max abs diff: train=0.0, val=0.0.
- Train no-collab abs diff=1.881959632e-05, PAD top2 abs diff=1.794981764e-05, random abs diff mean=2.903804519e-05; preliminary pass=False.
- Train PAD top2 CE=0.0002581242, bottom2 CE=0.0002466201, shuffled CE=0.0002562507, random mean CE=0.0002470063.
- Val no-collab abs diff=0.001043763347, PAD top2 abs diff=0.001318222217, random abs diff mean=0.001695952504; preliminary pass=False.
- Val PAD top2 CE=0.1577833134, bottom2 CE=0.1581670837, shuffled CE=0.1568494840, random mean CE=0.1586489953.

Decision:
- Do not start current DCA boundary-strengthening training from this gate.
- Retain the result as boundary-condition evidence: DCA/source prompts perturb final logits, but PAD-ranked source knowledge is not cleanly better than random/bottom/shuffled controls.
- This does not permanently exclude sample-conditioned prompt/source training; that would require a new manifest and D4 validation.

Interpretation:
- The collaborative branch is not completely ignored, because no-collab and source replacement do move the output.
- The source-ranking signal is not credible enough for a method claim: random produces larger perturbations, and shuffled/bottom controls match or beat PAD top2 on CE.
