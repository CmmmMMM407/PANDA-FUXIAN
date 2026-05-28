# Innovation Selector Gate Notes

Date: 2026-05-24
Branch: innovation/reliability-disagreement

Implemented selector entry points:

- `--selector_mode panda_gumbel`: original PANDA behavior.
- `--selector_mode deterministic`: training keeps Gumbel exploration; eval/test uses deterministic top-k over PAD logits.
- `--selector_mode reliability`: uses detached branch disagreement and fusion uncertainty to compute sample reliability/disagreement, fits train-split domain reliability means, then subtracts `lambda * reliability_distance(sample, source_domain)` from PAD logits. Training uses Gumbel over adjusted logits; eval/test uses deterministic top-k over adjusted logits.

Sanity checks completed:

- `python -m py_compile main.py run.py model/PANDA.py tools/run_panda_innovation_sanity.py tools/evaluate_panda_selector_variants.py`
- `python tools/run_panda_innovation_sanity.py --dataset weibo21 --batch-size 2 --modes deterministic reliability --gpu 0`

Held-checkpoint quick gate:

```bash
python tools/evaluate_panda_selector_variants.py \
  --datasets weibo21 \
  --seeds 42 \
  --splits val test \
  --modes panda_gumbel deterministic reliability \
  --batch-size 32 \
  --num-workers 0 \
  --reliability-lambda 0.05 \
  --overwrite
```

Main observation:

- On Weibo-21 seed42 held PANDA checkpoint, deterministic eval and reliability lambda=0.05 do not change Macro-F1/Accuracy relative to original Gumbel evaluation.
- Gumbel vs deterministic changes selected neighbors for most samples, but this rarely changes final labels. Deterministic vs reliability lambda=0.05 changes only a small number of selected-neighbor sets and no labels.
- This suggests the first full method experiment should test whether training-time reliability-aware selection changes representations/heads, not just inference-time reranking. It also motivates stronger lambda/grid ablations on validation before any formal test interpretation.

Important boundary:

- Reliability domain statistics are unsupervised and fitted from the train split only in this quick gate. Test labels are not used for selector weights, prototypes, or lambda selection.
