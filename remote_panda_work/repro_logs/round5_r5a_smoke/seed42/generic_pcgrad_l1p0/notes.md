# generic_pcgrad_l1p0

Dataset: weibo21
Seed: 42
Epochs: 5
Created at: 2026-05-26T22:06:07+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 42 --num_workers 0 --selector_mode deterministic_train --skip_final_test --aux_loss_weight 1.0 --r5a_grad_mode generic_pcgrad --save_param_dir param_model/round5_r5a_smoke/generic_pcgrad_l1p0 --r5a_log_dir repro_logs/round5_r5a_smoke/seed42/generic_pcgrad_l1p0 
