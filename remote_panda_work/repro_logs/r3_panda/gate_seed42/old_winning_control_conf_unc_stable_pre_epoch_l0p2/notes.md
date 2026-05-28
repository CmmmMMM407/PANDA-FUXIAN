# old_winning_control_conf_unc_stable_pre_epoch_l0p2

Dataset: weibo21
Seed: 42
Epochs: 5
Batch size: 32
LR: 1e-4
Early stop: 6
Created at: 2026-05-25T15:10:16+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 42 --num_workers 0 --selector_mode reliability --reliability_signal confidence_uncertainty --reliability_lambda 0.2 --reliability_gating stable_source_reward --reliability_stats_mode pre_epoch --save_param_dir param_model/r3_panda_gate_seed42/old_winning_control_conf_unc_stable_pre_epoch_l0p2 
