# Round 5 Gate-0 Deep Analysis

Date: 2026-05-26

Scope: Weibo-21 seed42 train/val-only Gate-0. No test split was exported,
opened, or used for decision making.

## Executive Conclusion

Round 5 Gate-0 supports the stop-loss decision, but the positive labels must be
read conservatively.

- G0-E and G0-S are No-Go results for current frozen/probe claim_scope.
- G0-A shows a real image-branch/final gradient conflict signal, but its
  low-margin/error association is weak and batch-level only.
- G0-D exposes destructive low-margin sensitivity rather than a usable
  boundary-stress method.
- R5-Prime, R5-A+D, and R5-S remain Not-Unlocked, not D4-failed combination
  mechanisms. The only defensible next experiment under this protocol is a
  single R5-A branch-final gradient-consistency smoke, with strong generic
  gradient and aux-loss controls.

## Detailed Findings

### G0-A: Real Image-Branch Conflict, Weak Mechanism Association

Evidence:

- Image branch conflict rate: `52/154 = 0.337662`.
- Image strong conflict rate `cos < -0.1`: `0.201299`.
- Image mean cosine: `0.072684`.
- Fusion branch conflict rate: `0.110390`.
- Text branch conflict rate: `0.019481`.

Interpretation:

The branch asymmetry is the strongest positive signal: image auxiliary BCE often
pushes against final BCE, while text is almost always aligned and fusion is
mostly aligned.

However, the enrichment evidence is thin:

- Image conflict low-margin batch rate is `0.780649` versus non-conflict
  `0.764277`, only `+1.64pp`.
- Image conflict error batch rate is `0.529447` versus non-conflict `0.517749`,
  only `+1.17pp`.
- Fusion low-margin rates are essentially tied: `0.770221` versus `0.769754`.
- Text goes the opposite direction: `0.718750` versus `0.770820`.

Important caveat:

G0-A records gradients in `model.train()` mode, while the common frozen metadata
used for margin/error context was exported in eval mode. The train q25
low-margin threshold is `8.226344`; under this threshold, `68.13%` of val samples
are counted low-margin. Therefore, "low-margin enriched" should not be written
as a precise sample-level mechanism. It is at most a weak batch-level association.

The `g0a_gradient_conflict_by_domain.csv` table is also batch-dominant-domain
aggregation, not per-sample per-domain evidence. Domain 8 dominates 86 batches,
while several domains have only 1-7 dominant batches, so it cannot support a
stable per-domain mechanism claim.

Additional pattern:

The image conflict signal is branch-specific but not domain-clean. Dominant
domain 8 accounts for `86/154` batches with image conflict rate `0.372093`,
while small dominant-domain buckets fluctuate widely, for example domain 3 has
only 5 batches and conflict rate `0.600000`. This is useful as a warning: R5-A
should target the image branch first, but should not introduce domain-specific
branch rules from this Gate-0 evidence.

### G0-D: Boundary Sensitivity Is Destructive

Evidence:

- `h_di` boundary shrink changes 24 val labels, with 7 wrong->correct and
  17 correct->wrong.
- `h_final` boundary shrink has the same 24 changed labels, also 7/17.
- `h_collab` boundary shrink changes 0 labels.
- `h_di` mean absolute logit delta: `0.839341`.
- `h_final` mean absolute logit delta: `0.903701`.
- `h_collab` mean absolute logit delta: `0.019702`.
- `h_di` boundary shrink F1/Acc: `0.939832/0.939837`, below original
  `0.956086/0.956098`.

Interpretation:

G0-D confirms that the final boundary is sensitive around the `h_di/h_final`
path, while the DCA/source prompt component `h_collab` is weak. This supports
the diagnosis that source/prompt knowledge is a late weak bias.

But it does not support R5-D as a training direction yet. The perturbation
mostly destroys correct predictions and lowers the main metrics. Treat G0-D as
boundary-fragility evidence only, not as a positive boundary-stress candidate.

Additional pattern:

The fragility is localized but not constructive. `h_di/h_final` boundary shrink
has overall flip rate `0.039024`, low-margin flip rate `0.057279`, and
non-low-margin flip rate `0.0`; so the low-margin boundary is genuinely thin.
However, the net effect is negative. The `h_final` random same-norm control
changes only 1 label and it is `1 wrong->correct / 0 correct->wrong`, with
F1/Acc `0.957715/0.957724`. This single-row control is not enough to promote a
random perturbation method, but it is enough to warn that any future boundary
stress claim must beat generic same-norm / VAT / SAM style controls.

### G0-E: Frozen Branch Evidential Arbitration Fails Cleanly

Evidence:

- Original final F1/Acc: `0.956086/0.956098`.
- Branch evidential arbitration F1/Acc: `0.933129/0.933333`.
- Flip audit: 5 wrong->correct, 19 correct->wrong.
- Low-margin delta F1: `-0.034826`.
- Weak-domain delta F1: `-0.051666`.
- Shuffled branch-logit control F1: `0.933152`, slightly above the primary.

Interpretation:

The frozen branch evidence probe does not prove ordered branch evidence is
usable. The primary is almost replicated by shuffled branch logits, which means
the learned arbitration is likely overfitting or acting as an unstable residual
around final logits. This closes the current frozen/probe R5-Prime path for now;
future branch-to-final evidential training would need a new manifest and D4.
It also reinforces the Round 3 ordinary-combiner risk.

Additional pattern:

Most branch/final frozen-arbitration variants are net destructive. Unweighted
final+aux mean changes 8 labels with `3 wrong->correct / 5 correct->wrong`;
weighted final+aux ordinary combiner changes 6 labels with `2/4`; branch
evidential arbitration changes 24 labels with `5/19`; shuffled branch logits
changes 26 labels with `6/20`. This means the failure is not one bad classifier
setting. Frozen branch-logit reuse systematically moves too many already-correct
samples across the boundary.

### G0-S: Source/Prompt Ranking Is Directionally Unstable

Evidence:

- DCA PAD top2 CE: `0.157783`.
- Shuffled PAD top2 CE: `0.156849`.
- Random pair mean CE: `0.158649`.
- PAD bottom2 pair CE: `0.158167`.
- Anchor deterministic DCA CE: `0.158358`.
- Forced shuffled top2 single CE is best among the summarized forced-view rows:
  `0.156251`.

Interpretation:

PAD top2 is not completely inert: it beats random-pair mean, bottom2 pair, and
anchor CE. But it loses to shuffled prompt/source controls. That is exactly the
failure mode seen in earlier source-view gates: prompt/source intervention can
move logits a little, but PAD ordering is not a clean mechanism.

Therefore, source/prompt work should not be reopened unless a genuinely
sample-conditioned prompt interaction first beats shuffled/random/static DCA
controls.

## Method Implications

The safest paper-level claim is diagnostic:

```text
PANDA's source/prompt/reliability/auxiliary signals contain useful diagnostic
information, but most of them are insulated from or too late for the final
decision boundary. The only remaining positive training-dynamics signal is an
image-branch/final gradient conflict candidate.
```

Do not claim:

- branch-evidential arbitration is effective;
- source/prompt ranking is effective;
- low-margin boundary stress is already useful;
- G0-A proves a stable weak-domain or low-margin mechanism.

## Revised Next Step

Only R5-A single-branch smoke is defensible, and it needs a stricter prelude:

1. Re-run or extend the G0-A diagnostic with an explicit mode caveat:
   train-mode gradients are primary, but eval-mode/no-dropout gradient probing
   should be reported as a robustness check if feasible.
2. Focus on image-branch/final conflict first. Do not average text/image/fusion
   if the conflict is branch-specific.
3. Pre-register controls before running:
   deterministic_train baseline, aux weight sweep, generic PCGrad/CAGrad,
   random-sign gradient penalty, same-forward-budget control, and no-new-module
   extra-epoch/lr control.
4. Promotion rule: R5-A must improve Macro-F1/Acc without being matched by
   generic gradient methods, and gradient conflict reduction must align with
   wrong->correct > correct->wrong.

If R5-A fails this smoke, the current Round 5 old PAD/source/reliability/offline-
boundary tuning path should stop rather than drift. That stop-loss does not
permanently exclude R5 reserve or combination mechanisms without a new manifest
and the required D-level validation.
