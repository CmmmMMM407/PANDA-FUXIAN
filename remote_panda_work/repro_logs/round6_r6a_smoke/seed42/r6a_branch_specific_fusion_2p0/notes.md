# r6a_branch_specific_fusion_2p0

Dataset: weibo21
Seed: 42
Epochs: 5
Created at: 2026-05-28T02:21:39+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 42 --num_workers 0 --selector_mode deterministic_train --skip_final_test --r6a_aux_text_weight 1.0 --r6a_aux_image_weight 1.0 --r6a_aux_fusion_weight 2.0 --r5a_grad_mode none --save_param_dir param_model/round6_r6a_smoke/r6a_branch_specific_fusion_2p0 --r5a_log_dir repro_logs/round6_r6a_smoke/seed42/r6a_branch_specific_fusion_2p0 
