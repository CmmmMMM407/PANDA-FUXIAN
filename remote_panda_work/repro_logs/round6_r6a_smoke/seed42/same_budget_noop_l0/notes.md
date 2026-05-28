# same_budget_noop_l0

Dataset: weibo21
Seed: 42
Epochs: 5
Created at: 2026-05-28T00:56:27+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 42 --num_workers 0 --selector_mode deterministic_train --skip_final_test --aux_loss_weight 0.0 --r5a_grad_mode same_budget_noop --save_param_dir param_model/round6_r6a_smoke/same_budget_noop_l0 --r5a_log_dir repro_logs/round6_r6a_smoke/seed42/same_budget_noop_l0 
