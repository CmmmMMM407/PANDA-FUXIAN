# Round 7 D4-lite Summary

Scope: Weibo-21 seed42 train/val-only short dynamics. This is not formal D4.

- Status: `COMPLETED`
- Test split exported: `false`
- Test used for decision: `false`
- Checkpoint written: `false`
- Train budget: `1` epoch(s), max train batches `40`

## Variants

### deterministic_lite
- family: `baseline`
- train_loss_first/last: `0.989104151725769` / `0.6078928112983704`
- val macro_f1/accuracy/auc: `0.6081640922049744` / `0.6471544715447154` / `0.8310206240084611`
- val ece/brier/hce: `0.08008607485430026` / `0.2116194639366036` / `0.0`

### r7a_composite_risk_lite
- family: `R7-A`
- train_loss_first/last: `1.0052744150161743` / `0.567130982875824`
- val macro_f1/accuracy/auc: `0.7323293871866295` / `0.7398373983739838` / `0.8663670015864622`
- val ece/brier/hce: `0.06507919920169238` / `0.17379412990578716` / `0.0`

### r7a_confidence_only_control
- family: `R7-A`
- train_loss_first/last: `1.0276482105255127` / `0.6450449824333191`
- val macro_f1/accuracy/auc: `0.7056861034617603` / `0.7154471544715447` / `0.8367107350608144`
- val ece/brier/hce: `0.02862936638719666` / `0.18627223337020724` / `0.0`

### r7a_random_risk_control
- family: `R7-A`
- train_loss_first/last: `1.0105223655700684` / `0.6978646516799927`
- val macro_f1/accuracy/auc: `0.6933286828760534` / `0.7024390243902439` / `0.8270333157059757`
- val ece/brier/hce: `0.043481573220190944` / `0.18803936333405338` / `0.0`

### r7a_shuffled_risk_control
- family: `R7-A`
- train_loss_first/last: `1.005367636680603` / `0.5460149049758911`
- val macro_f1/accuracy/auc: `0.6807801947988864` / `0.6959349593495935` / `0.8650343733474353`
- val ece/brier/hce: `0.05866580421362464` / `0.1820044776035122` / `0.0`

### r7d_sample_aux_curriculum_lite
- family: `R7-D`
- train_loss_first/last: `1.0605896711349487` / `0.6470388174057007`
- val macro_f1/accuracy/auc: `0.6305924144055595` / `0.6601626016260163` / `0.8365943945002644`
- val ece/brier/hce: `0.06363133453741307` / `0.19892280873433488` / `0.0`

### r7d_static_aux_2p0_control
- family: `R7-D`
- train_loss_first/last: `1.227064609527588` / `0.7356144189834595`
- val macro_f1/accuracy/auc: `0.7365207891523682` / `0.7398373983739838` / `0.8371972501322051`
- val ece/brier/hce: `0.07917980932123292` / `0.18011011252975348` / `None`

### r7d_random_aux_control
- family: `R7-D`
- train_loss_first/last: `1.12430739402771` / `0.7788920998573303`
- val macro_f1/accuracy/auc: `0.5842478461176512` / `0.6308943089430894` / `0.821565309360127`
- val ece/brier/hce: `0.10404292691529282` / `0.2220791462130774` / `0.0`

### r7d_shuffled_aux_control
- family: `R7-D`
- train_loss_first/last: `1.0791839361190796` / `0.8030937314033508`
- val macro_f1/accuracy/auc: `0.6821670291647437` / `0.6959349593495935` / `0.8078476996298255`
- val ece/brier/hce: `0.08562854460584438` / `0.20517821943408904` / `None`

## Interpretation

- D4-lite can demote a setup as not worth formal D4, but cannot write training implementation No-Go.