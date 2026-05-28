# weibo21_seed2026_deterministic_eval_l0

Dataset: weibo21
Seed: 2026
Epochs: 5
Batch size: 32
LR: 1e-4
Early stop: 6
Created at: 2026-05-24T23:17:46+08:00

Command:
/root/miniconda3/bin/python main.py --dataset weibo21 --model_name FTmodel --gpu 0 --batchsize 32 --lr 1e-4 --epoch 5 --early_stop 6 --seed 2026 --num_workers 0 --selector_mode deterministic --reliability_lambda 0.0 
