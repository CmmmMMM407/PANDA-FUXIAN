# static_aux_weight_0p0

Dataset: weibo21
Seed: 42
Epochs: 5
Created at: 2026-05-28T01:02:50+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 42 --num_workers 0 --selector_mode deterministic_train --skip_final_test --aux_loss_weight 0.0 --r5a_grad_mode none --save_param_dir param_model/round6_r6a_smoke/static_aux_weight_0p0 --r5a_log_dir repro_logs/round6_r6a_smoke/seed42/static_aux_weight_0p0 
