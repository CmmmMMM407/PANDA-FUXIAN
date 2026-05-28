# Round 7 D3.5 Gradient Sanity Summary

Scope: Weibo-21 seed42 train-only real PANDA batches. No optimizer step, no checkpoint, no test.

- Status: `COMPLETED`
- Train batches: `3` requested, `3` observed
- Test split exported: `false`
- Test used for decision: `false`

## Interpretation

- D3.5 only checks gradient reachability and control moat on real computation graphs.
- It cannot judge validation performance or close training-time methods.

## Candidate Loss Means

### R7-A::ce_reference
- mean_loss_value: `0.10858417550722758`
- mean_final_classifier_grad_norm: `1.0717371205488841`
- mean_h_final_grad_norm: `0.24685371915499368`
- mean_final_classifier_cosine_vs_ce: `0.9999999006589254`
- mean_h_final_cosine_vs_ce: `1.0`
- mean_h_final_high_over_low_grad_ratio: `2.6607569058736167`
- mean_text_branch_grad_norm: `10.097164630889893`
- mean_image_branch_grad_norm: `11.60466464360555`
- mean_fusion_branch_grad_norm: `4.269359310468038`

### R7-A::confidence_only_margin_control
- mean_loss_value: `0.09893629622335236`
- mean_final_classifier_grad_norm: `1.9752720197041829`
- mean_h_final_grad_norm: `0.4260733127593994`
- mean_final_classifier_cosine_vs_ce: `0.9855302572250366`
- mean_h_final_cosine_vs_ce: `0.9375077188014984`
- mean_h_final_high_over_low_grad_ratio: `1.884891192118327`
- mean_text_branch_grad_norm: `17.077035268147785`
- mean_image_branch_grad_norm: `20.841718673706055`
- mean_fusion_branch_grad_norm: `6.255149761835734`

### R7-A::random_risk_margin_control
- mean_loss_value: `0.001954883492241303`
- mean_final_classifier_grad_norm: `0.4398773020754258`
- mean_h_final_grad_norm: `0.08486112781489889`
- mean_final_classifier_cosine_vs_ce: `0.9855302572250366`
- mean_h_final_cosine_vs_ce: `0.9375077188014984`
- mean_h_final_high_over_low_grad_ratio: `1.884891192118327`
- mean_text_branch_grad_norm: `3.539799769719442`
- mean_image_branch_grad_norm: `3.600952833890915`
- mean_fusion_branch_grad_norm: `0.43603018919626874`

### R7-A::risk_anti_overconfidence
- mean_loss_value: `0.0022188276828577123`
- mean_final_classifier_grad_norm: `0.002765132191901406`
- mean_h_final_grad_norm: `0.0005940159608144313`
- mean_final_classifier_cosine_vs_ce: `-0.12061997689306736`
- mean_h_final_cosine_vs_ce: `0.17254521449406943`
- mean_h_final_high_over_low_grad_ratio: `1.4888409574826558`
- mean_text_branch_grad_norm: `0.024911879561841488`
- mean_image_branch_grad_norm: `0.030203454817334812`
- mean_fusion_branch_grad_norm: `0.005289337985838453`

### R7-A::risk_consistency
- mean_loss_value: `0.0037529229496916137`
- mean_final_classifier_grad_norm: `0.06342725952466328`
- mean_h_final_grad_norm: `0.012103945792963108`
- mean_final_classifier_cosine_vs_ce: `-0.32636334498723346`
- mean_h_final_cosine_vs_ce: `-0.31475013494491577`
- mean_h_final_high_over_low_grad_ratio: `2.579376300175985`
- mean_text_branch_grad_norm: `0.49752838909626007`
- mean_image_branch_grad_norm: `0.5213627939422926`
- mean_fusion_branch_grad_norm: `0.11030011375745137`

### R7-A::risk_margin
- mean_loss_value: `0.0742022196451823`
- mean_final_classifier_grad_norm: `1.4814539750417073`
- mean_h_final_grad_norm: `0.3195549746354421`
- mean_final_classifier_cosine_vs_ce: `0.9855303168296814`
- mean_h_final_cosine_vs_ce: `0.9375077188014984`
- mean_h_final_high_over_low_grad_ratio: `1.884891192118327`
- mean_text_branch_grad_norm: `12.80767567952474`
- mean_image_branch_grad_norm: `15.631675720214844`
- mean_fusion_branch_grad_norm: `4.6913619836171465`

### R7-A::shuffled_risk_margin_control
- mean_loss_value: `0.02900387595097224`
- mean_final_classifier_grad_norm: `1.0863609910011292`
- mean_h_final_grad_norm: `0.221648578842481`
- mean_final_classifier_cosine_vs_ce: `0.9855304062366486`
- mean_h_final_cosine_vs_ce: `0.9375077486038208`
- mean_h_final_high_over_low_grad_ratio: `1.8848913510640461`
- mean_text_branch_grad_norm: `9.058975378672281`
- mean_image_branch_grad_norm: `10.146183649698893`
- mean_fusion_branch_grad_norm: `2.2291454474131265`

### R7-B::agreement_kd
- mean_loss_value: `0.20658153543869653`
- mean_final_classifier_grad_norm: `0.32696304221947986`
- mean_h_final_grad_norm: `0.0706406223277251`
- mean_final_classifier_cosine_vs_ce: `0.015062109877665838`
- mean_h_final_cosine_vs_ce: `0.2974955340226491`
- mean_h_final_high_over_low_grad_ratio: `1.2640824516614277`
- mean_text_branch_grad_norm: `2.540850122769674`
- mean_image_branch_grad_norm: `3.338141123453776`
- mean_fusion_branch_grad_norm: `0.577042688926061`

### R7-B::disagreement_margin
- mean_loss_value: `0.09893629622335236`
- mean_final_classifier_grad_norm: `1.9752720197041829`
- mean_h_final_grad_norm: `0.4260733127593994`
- mean_final_classifier_cosine_vs_ce: `0.9855302572250366`
- mean_h_final_cosine_vs_ce: `0.9375077188014984`
- mean_h_final_high_over_low_grad_ratio: `1.884891192118327`
- mean_text_branch_grad_norm: `17.077035268147785`
- mean_image_branch_grad_norm: `20.841718673706055`
- mean_fusion_branch_grad_norm: `6.255149761835734`

### R7-B::wrong_branch_suppression
- mean_loss_value: `0.009319759119534865`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.0`
- mean_text_branch_grad_norm: `0.9642635136842728`
- mean_image_branch_grad_norm: `1.583705763022105`
- mean_fusion_branch_grad_norm: `0.29798001050949097`

### R7-C::all_sample_supcon_control
- mean_loss_value: `1.5330862998962402`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.023129820202787716`
- mean_h_final_cosine_vs_ce: `0.21075750887393951`
- mean_h_final_high_over_low_grad_ratio: `0.8076853553454081`
- mean_text_branch_grad_norm: `0.9780965646107992`
- mean_image_branch_grad_norm: `0.8609143098195394`
- mean_fusion_branch_grad_norm: `0.868349552154541`

### R7-C::hard_region_supcon
- mean_loss_value: `1.5330862998962402`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.023129820202787716`
- mean_h_final_cosine_vs_ce: `0.21075750887393951`
- mean_h_final_high_over_low_grad_ratio: `0.8076853553454081`
- mean_text_branch_grad_norm: `0.9780965646107992`
- mean_image_branch_grad_norm: `0.8609143098195394`
- mean_fusion_branch_grad_norm: `0.868349552154541`

### R7-C::interclass_margin
- mean_loss_value: `0.45489587386449176`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.045805949717760086`
- mean_h_final_cosine_vs_ce: `0.11495739842454593`
- mean_h_final_high_over_low_grad_ratio: `0.634599526723226`
- mean_text_branch_grad_norm: `1.863950788974762`
- mean_image_branch_grad_norm: `1.764443278312683`
- mean_fusion_branch_grad_norm: `1.615186095237732`

### R7-C::random_hard_supcon_control
- mean_loss_value: `1.3395660320917766`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.030742016931374867`
- mean_h_final_cosine_vs_ce: `0.1653645453043282`
- mean_h_final_high_over_low_grad_ratio: `0.6182711323102316`
- mean_text_branch_grad_norm: `1.3859758774439495`
- mean_image_branch_grad_norm: `1.1654770374298096`
- mean_fusion_branch_grad_norm: `1.0219067732493083`

### R7-D::random_aux_weight_control
- mean_loss_value: `0.36459551254908246`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.0`
- mean_text_branch_grad_norm: `23.17522939046224`
- mean_image_branch_grad_norm: `27.196719805399578`
- mean_fusion_branch_grad_norm: `8.324060832460722`

### R7-D::sample_reliability_aux
- mean_loss_value: `0.25043268501758575`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.0`
- mean_text_branch_grad_norm: `14.644867579142252`
- mean_image_branch_grad_norm: `20.072272936503094`
- mean_fusion_branch_grad_norm: `4.5360486681262655`

### R7-D::shuffled_aux_weight_control
- mean_loss_value: `0.25190172096093494`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.0`
- mean_text_branch_grad_norm: `15.358749071756998`
- mean_image_branch_grad_norm: `18.552210489908855`
- mean_fusion_branch_grad_norm: `4.521706600983937`

### R7-D::static_aux_2p0_control
- mean_loss_value: `0.48114221294720966`
- mean_final_classifier_grad_norm: `0.0`
- mean_h_final_grad_norm: `0.0`
- mean_text_branch_grad_norm: `28.60334014892578`
- mean_image_branch_grad_norm: `36.93550491333008`
- mean_fusion_branch_grad_norm: `9.01421044766903`
