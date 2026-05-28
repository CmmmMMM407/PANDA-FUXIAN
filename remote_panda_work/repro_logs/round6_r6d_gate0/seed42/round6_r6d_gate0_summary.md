# Round 6 R6-D Gate-0 Summary

Decision: `No-Go`

Scope: D3 train/val-only cross-architecture complementarity; no training; no test.

Rows: train `4926`, val `615`.

PANDA original F1/Acc/AUC: `0.956086/0.956098/0.987372`.
Best primary `confidence_gate_dammfnd` F1/Acc/AUC: `0.951190/0.951220/0.985119`, W2C/C2W `8/11`.
Best control `mean_probability_ensemble` F1/Acc/AUC: `0.947937/0.947967/0.987985`.
Oracle recoverable PANDA errors: `12` / `27`.

Decision reasons:
- best_primary_below_panda
- best_primary_flip_not_net_positive
