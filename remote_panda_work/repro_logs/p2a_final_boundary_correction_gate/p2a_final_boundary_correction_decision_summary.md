# P2-A Final-Boundary Correction Gate

Dataset/seed: `weibo21` / `42`

Decision: **No-Go**

Test used for decision: `False`

## Baseline

{
  "macro_f1": 0.9560859504132231,
  "accuracy": 0.9560975609756097,
  "auc": 0.9873823373876256,
  "ece": 0.03489726617958571,
  "brier": 0.0387069766720739,
  "high_conf_error_rate": 0.026690391459074734,
  "weak_domain_macro_f1": 0.930849478390462
}

## Best Primary

Variant: `final_plus_aux_reliability_domain`

{
  "macro_f1": 0.9298408984185351,
  "accuracy": 0.9300813008130081,
  "auc": 0.9492332099418297,
  "ece": 0.06123270847821739,
  "brier": 0.06361359668307055,
  "high_conf_error_rate": 0.06208053691275168,
  "weak_domain_macro_f1": 0.8706031085000372,
  "support_better_count": 0.0
}

## Best Strong Control

Variant: `final_plus_random_features_seed1`

{
  "macro_f1": 0.9544511924159385,
  "accuracy": 0.9544715447154472,
  "auc": 0.9874246430460074,
  "ece": 0.021731181381003127,
  "brier": 0.03839216814743441,
  "high_conf_error_rate": 0.022018348623853212,
  "weak_domain_macro_f1": 0.9136904761904762,
  "support_better_count": 4.0
}

## Interpretation

The best reliability-conditioned correction does not clear the pre-registered minimal gate against calibration/domain/random/shuffled controls. Do not promote P2-A to a training mainline from this evidence.
