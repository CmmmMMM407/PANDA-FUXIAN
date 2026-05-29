# Round13 ADWA-PANDA D3.5 Gradient Sanity

Scope: Weibo-21 seed42 train-only real PANDA batches. No optimizer step, no checkpoint, no val/test.

- Decision: `D3.5-Feasible-A`
- Observed batches: `5`
- Test split exported: `false`
- Test used for decision: `false`

## Loss Means

### adwa_panda
- mean_loss_value: `0.7922310523688794`
- mean_h_final_grad_norm: `0.2270316097768955`
- mean_final_classifier_grad_norm: `0.9494189196266234`
- mean_text_branch_grad_norm: `27.013236582279205`
- mean_image_branch_grad_norm: `37.109008646011354`
- mean_fusion_branch_grad_norm: `11.297863647341728`
- mean_text_aux_head_grad_norm: `1.034000251814723`
- mean_image_aux_head_grad_norm: `0.8308007583022118`
- mean_fusion_aux_head_grad_norm: `0.4556093056453392`
- mean_raw_text_weight: `0.9988193869590759`
- mean_raw_image_weight: `1.0069983720779419`
- mean_raw_fusion_weight: `0.9941822052001953`
- rate_guard_active: `0.6`

### detached_aux_control
- mean_loss_value: `0.7921605817973614`
- mean_h_final_grad_norm: `0.2270316097768955`
- mean_final_classifier_grad_norm: `0.9494189196266234`
- mean_text_branch_grad_norm: `8.409668374061585`
- mean_image_branch_grad_norm: `11.819108510017395`
- mean_fusion_branch_grad_norm: `4.531881694495678`
- mean_text_aux_head_grad_norm: `0.0`
- mean_image_aux_head_grad_norm: `0.0`
- mean_fusion_aux_head_grad_norm: `0.0`

### final_ce
- mean_loss_value: `0.21548239983385428`
- mean_h_final_grad_norm: `0.2270316097768955`
- mean_final_classifier_grad_norm: `0.9494189196266234`
- mean_text_branch_grad_norm: `8.298979759961366`
- mean_image_branch_grad_norm: `11.522740311920643`
- mean_fusion_branch_grad_norm: `4.5340616181492805`
- mean_text_aux_head_grad_norm: `0.0`
- mean_image_aux_head_grad_norm: `0.0`
- mean_fusion_aux_head_grad_norm: `0.0`

### generic_dwa_proxy
- mean_loss_value: `0.30518811419606207`
- mean_h_final_grad_norm: `0.0565313751460053`
- mean_final_classifier_grad_norm: `0.2378269296779763`
- mean_text_branch_grad_norm: `9.920373845100404`
- mean_image_branch_grad_norm: `12.801468348503112`
- mean_fusion_branch_grad_norm: `3.670023813843727`
- mean_text_aux_head_grad_norm: `0.4302857632748783`
- mean_image_aux_head_grad_norm: `0.3029161483049393`
- mean_fusion_aux_head_grad_norm: `0.16765506841475145`

### static_aux_2p0
- mean_loss_value: `0.7921605817973614`
- mean_h_final_grad_norm: `0.2270316097768955`
- mean_final_classifier_grad_norm: `0.9494189196266234`
- mean_text_branch_grad_norm: `27.015733695030214`
- mean_image_branch_grad_norm: `37.08457353115082`
- mean_fusion_branch_grad_norm: `11.297870515286922`
- mean_text_aux_head_grad_norm: `1.0342136319726705`
- mean_image_aux_head_grad_norm: `0.8301716066896916`
- mean_fusion_aux_head_grad_norm: `0.45563581043388696`

