# Round 6 R6-B Branch Feature Export

Status: train/val branch features exported.

Rules:
- Test split is not accepted.
- This is frozen inference/export only, not training.
- `h_text + h_image + h_fusion` is verified against exported `h_di`.
- The export enables feature-level R6-B Gate-0; proxy branch-logit stacking alone is not enough.
