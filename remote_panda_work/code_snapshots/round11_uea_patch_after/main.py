
import os
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--dataset', default='weibo21') # weibo21 %% weibo ## FINE
parser.add_argument('--model_name', default='clean_vib')
parser.add_argument('--epoch', type=int, default=50)
parser.add_argument('--max_len', type=int, default=197)
parser.add_argument('--num_workers', type=int, default=4)
parser.add_argument('--early_stop', type=int, default=6)
parser.add_argument('--bert_vocab_file', default='./pretrained_model/chinese_roberta_wwm_base_ext_pytorch/vocab.txt')
parser.add_argument('--roberta_vocab_file', default='./pretrained_model/roberta/vocab.json')
parser.add_argument('--root_path', default='./data/')
parser.add_argument('--bert', default='./pretrained_model/chinese_roberta_wwm_base_ext_pytorch')
parser.add_argument('--roberta', default='./pretrained_model/roberta')
parser.add_argument('--batchsize', type=int, default=64) # 64 is best
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--gpu', default='0')
parser.add_argument('--bert_emb_dim', type=int, default=768)
parser.add_argument('--w2v_emb_dim', type=int, default=200)
parser.add_argument('--lr', type=float, default=0.001)
parser.add_argument('--emb_type', default='bert')
parser.add_argument('--w2v_vocab_file', default='./pretrained_model/w2v/Tencent_AILab_Chinese_w2v_model.kv')
parser.add_argument('--save_param_dir', default= './param_model')
parser.add_argument('--skip_final_test', action='store_true',
                    help='Skip the final test_loader evaluation after training; use for val-only method selection gates.')
parser.add_argument('--selector_mode', default='panda_gumbel',
                    choices=[
                        'panda_gumbel',
                        'gumbel',
                        'deterministic',
                        'deterministic_train',
                        'reliability',
                        'regret_soft_pad_only',
                        'regret_soft_adapter_l0',
                        'regret_soft_adapter_neg',
                        'regret_soft_adapter_neg_reliability',
                        'regret_soft_adapter_neg_balance',
                        'regret_soft_adapter_neg_group',
                        'regret_soft_adapter_neg_shuffled'
                    ])
parser.add_argument('--reliability_signal', default='branch_fusion',
                    choices=[
                        'branch',
                        'fusion',
                        'branch_fusion',
                        'clip',
                        'clip_dissimilarity',
                        'branch_fusion_clip',
                        'confidence_uncertainty',
                        'overconfidence',
                        'random'
                    ])
parser.add_argument('--reliability_lambda', type=float, default=0.05)
parser.add_argument('--reliability_gating', default='distance',
                    choices=['distance', 'high_unc_penalty', 'stable_source_reward'])
parser.add_argument('--reliability_stats_mode', default='online',
                    choices=['online', 'prefit', 'pre_epoch', 'ema'])
parser.add_argument('--reliability_ema_momentum', type=float, default=0.9)
parser.add_argument('--selection_margin_lambda', type=float, default=0.0)
parser.add_argument('--selection_margin', type=float, default=0.1)
parser.add_argument('--aux_loss_weight', type=float, default=1.0,
                    help='Multiplier for mean(text/image/fusion) auxiliary BCE losses.')
parser.add_argument('--aux_text_weight', '--r6a_aux_text_weight', dest='aux_text_weight', type=float, default=None,
                    help='Optional absolute text-branch auxiliary BCE weight; defaults to aux_loss_weight.')
parser.add_argument('--aux_image_weight', '--r6a_aux_image_weight', dest='aux_image_weight', type=float, default=None,
                    help='Optional absolute image-branch auxiliary BCE weight; defaults to aux_loss_weight.')
parser.add_argument('--aux_fusion_weight', '--r6a_aux_fusion_weight', dest='aux_fusion_weight', type=float, default=None,
                    help='Optional absolute fusion-branch auxiliary BCE weight; defaults to aux_loss_weight.')
parser.add_argument('--aux_schedule', '--r6a_aux_schedule', dest='aux_schedule', default='constant',
                    choices=['constant', 'linear_ramp_up', 'linear_ramp_down', 'cosine_ramp_up', 'cosine_ramp_down'],
                    help='Scalar schedule applied to the effective auxiliary branch weights.')
parser.add_argument('--aux_schedule_start', '--r6a_aux_schedule_start', dest='aux_schedule_start', type=float, default=1.0,
                    help='Auxiliary schedule multiplier at the first optimization step.')
parser.add_argument('--aux_schedule_end', '--r6a_aux_schedule_end', dest='aux_schedule_end', type=float, default=1.0,
                    help='Auxiliary schedule multiplier at the last optimization step.')
parser.add_argument('--aux_label_mode', '--r6a_aux_label_mode', dest='aux_label_mode', default='true',
                    choices=['true', 'random', 'shuffled'],
                    help='Train-only auxiliary label control for R6-A; final loss always uses the true label.')
parser.add_argument('--aux_label_seed', '--r6a_aux_label_seed', dest='aux_label_seed', type=int, default=None,
                    help='Optional independent seed for random/shuffled auxiliary labels.')
parser.add_argument('--aux_random_label_seed', '--r6a_aux_random_label_seed', dest='aux_random_label_seed',
                    type=int, default=None,
                    help='Optional seed used only when aux_label_mode=random.')
parser.add_argument('--aux_shuffle_seed', '--r6a_aux_shuffle_seed', dest='aux_shuffle_seed',
                    type=int, default=None,
                    help='Optional seed used only when aux_label_mode=shuffled.')
parser.add_argument('--aux_feature_update_mode', '--r6a_aux_detach_mode', dest='aux_feature_update_mode',
                    default='normal', choices=['normal', 'detach'],
                    help='Use detach to prevent auxiliary losses from updating branch features.')
parser.add_argument('--aux_detach_features', '--r6a_aux_detach_features', '--r6a_aux_detach', dest='aux_detach_features',
                    action='store_true',
                    help='Compute auxiliary heads on detached branch features so aux loss does not update feature extractors.')
parser.add_argument('--aux_no_feature_update', '--r6a_aux_no_feature_update', dest='aux_no_feature_update',
                    action='store_true',
                    help='Alias for --aux_detach_features.')
parser.add_argument('--r5a_grad_mode', default='none',
                    choices=[
                        'none',
                        'same_budget_noop',
                        'image_project',
                        'generic_pcgrad',
                        'generic_cagrad',
                        'generic_gradnorm',
                        'generic_dwa',
                        'random_sign',
                        'dgl_branch_pcgrad',
                        'dgl_branch_conflict_drop'
                    ],
                    help='Round 5-A gradient-control mode for branch-final smoke tests.')
parser.add_argument('--r5a_log_dir', default=None,
                    help='Optional directory for R5-A training gradient telemetry.')
parser.add_argument('--r5a_log_interval', type=int, default=1,
                    help='Log one R5-A gradient telemetry row every N train steps.')
parser.add_argument('--uea_aux_mode', default='none',
                    choices=[
                        'none',
                        'utility_only',
                        'entropy',
                        'shuffled_utility',
                        'random_utility',
                        'reverse_utility',
                        'confidence',
                        'boundary_entropy'
                    ],
                    help='Round11 UEA per-sample branch auxiliary allocation mode.')
parser.add_argument('--uea_utility_csv', default=None,
                    help='Train-only branch utility CSV used by Round11 UEA allocation.')
parser.add_argument('--uea_alpha_max', type=float, default=0.5,
                    help='Maximum interpolation strength from uniform aux allocation to UEA branch allocation.')
parser.add_argument('--uea_weight_floor', type=float, default=1e-8,
                    help='Numerical floor for UEA branch allocation normalization.')
parser.add_argument('--uea_seed', type=int, default=None,
                    help='Optional seed for UEA shuffled/random controls; defaults to --seed.')
parser.add_argument('--uea_boundary_low_margin_quantile', type=float, default=0.25,
                    help='Train-only low-margin quantile for the legacy boundary entropy negative control.')
parser.add_argument('--uea_boundary_risk_quantile', type=float, default=0.75,
                    help='Train-only risk quantile for the legacy boundary entropy negative control.')
parser.add_argument('--regret_lambda', type=float, default=0.0)
parser.add_argument('--route_balance_lambda', type=float, default=0.0)
parser.add_argument('--regret_margin', type=float, default=0.0)
parser.add_argument('--router_tau_start', type=float, default=2.0)
parser.add_argument('--router_tau_end', type=float, default=1.0)
parser.add_argument('--adapter_dim', type=int, default=64)
parser.add_argument('--router_hidden', type=int, default=128)
args = parser.parse_args()
os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu

from run import Run
import torch
import numpy as np
import random

seed = args.seed
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

#
torch.cuda.manual_seed_all(seed)
torch.backends.cudnn.enabled = True


if args.emb_type == 'bert':
    emb_dim = args.bert_emb_dim
    vocab_file = args.bert_vocab_file
elif args.emb_type == 'w2v':
    emb_dim = args.w2v_emb_dim
    vocab_file = args.w2v_vocab_file
print('lr: {}; model name: {}; emb_type: {}; batchsize: {}; epoch: {}; gpu: {}; emb_dim: {}'.format(args.lr, args.model_name, args.emb_type,  args.batchsize, args.epoch, args.gpu, emb_dim))


config = {
        'use_cuda': True,
        'batchsize': args.batchsize,
        'max_len': args.max_len,
        'early_stop': args.early_stop,
        'num_workers': args.num_workers,
        'vocab_file': vocab_file,
        'emb_type': args.emb_type,
        'bert': args.bert,
        'root_path': args.root_path,
        'weight_decay': 5e-5,
        'model':
            {
            'mlp': {'dims': [384], 'dropout': 0.2}
            },
        'emb_dim': emb_dim,
        'lr': args.lr,
        'epoch': args.epoch,
        'model_name': args.model_name,
        'seed': args.seed,
        'save_param_dir': args.save_param_dir,
        'dataset':args.dataset,
        'skip_final_test': args.skip_final_test,
        'selector_mode': args.selector_mode,
        'reliability_signal': args.reliability_signal,
        'reliability_lambda': args.reliability_lambda,
        'reliability_gating': args.reliability_gating,
        'reliability_stats_mode': args.reliability_stats_mode,
        'reliability_ema_momentum': args.reliability_ema_momentum,
        'selection_margin_lambda': args.selection_margin_lambda,
        'selection_margin': args.selection_margin,
        'aux_loss_weight': args.aux_loss_weight,
        'aux_text_weight': args.aux_text_weight,
        'aux_image_weight': args.aux_image_weight,
        'aux_fusion_weight': args.aux_fusion_weight,
        'aux_schedule': args.aux_schedule,
        'aux_schedule_start': args.aux_schedule_start,
        'aux_schedule_end': args.aux_schedule_end,
        'aux_label_mode': args.aux_label_mode,
        'aux_label_seed': args.aux_label_seed,
        'aux_random_label_seed': args.aux_random_label_seed,
        'aux_shuffle_seed': args.aux_shuffle_seed,
        'aux_detach_features': args.aux_detach_features or args.aux_no_feature_update or args.aux_feature_update_mode == 'detach',
        'r5a_grad_mode': args.r5a_grad_mode,
        'r5a_log_dir': args.r5a_log_dir,
        'r5a_log_interval': args.r5a_log_interval,
        'uea_aux_mode': args.uea_aux_mode,
        'uea_utility_csv': args.uea_utility_csv,
        'uea_alpha_max': args.uea_alpha_max,
        'uea_weight_floor': args.uea_weight_floor,
        'uea_seed': args.seed if args.uea_seed is None else args.uea_seed,
        'uea_boundary_low_margin_quantile': args.uea_boundary_low_margin_quantile,
        'uea_boundary_risk_quantile': args.uea_boundary_risk_quantile,
        'regret_lambda': args.regret_lambda,
        'route_balance_lambda': args.route_balance_lambda,
        'regret_margin': args.regret_margin,
        'router_tau_start': args.router_tau_start,
        'router_tau_end': args.router_tau_end,
        'adapter_dim': args.adapter_dim,
        'router_hidden': args.router_hidden
        }




if __name__ == '__main__':
    Run(config = config).main()
