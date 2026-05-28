# regret_soft_adapter_neg_l0p05

Dataset: weibo21
Seed: 42
Epochs: 5
Batch size: 32
LR: 1e-4
Early stop: 6
Created at: 2026-05-25T15:35:31+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 42 --num_workers 0 --selector_mode regret_soft_adapter_neg --regret_lambda 0.05 --route_balance_lambda 0.0 --regret_margin 0.0 --router_tau_start 2.0 --router_tau_end 1.0 --adapter_dim 64 --router_hidden 128 --save_param_dir param_model/r3_panda_gate_seed42/regret_soft_adapter_neg_l0p05 
