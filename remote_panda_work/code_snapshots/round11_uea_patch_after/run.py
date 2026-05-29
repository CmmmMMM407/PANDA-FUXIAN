
import os
from utils.clip_dataloader_prompt import bert_data as weibo_data
from utils.weibo21_clip_prompt import bert_data as weibo21_data
from utils.FINE_clip_prompt import bert_data as FINE_data
from model.PANDA import Trainer as LPROMPTIMAGETrainer
from model.FTmodel2 import Trainer as LPROMPTIMAGETrainer2
from model.clean_vib import Trainer as LPROMPTIMAGETrainer3


class Run():
    def __init__(self,
                 config
                 ):
        self.configinfo = config

        self.use_cuda = config['use_cuda']
        self.model_name = config['model_name']
        self.lr = config['lr']
        self.batchsize = config['batchsize']
        self.emb_type = config['emb_type']
        self.emb_dim = config['emb_dim']
        self.max_len = config['max_len']
        self.num_workers = config['num_workers']
        self.vocab_file = config['vocab_file']
        self.early_stop = config['early_stop']
        self.bert = config['bert']
        self.root_path = config['root_path']
        self.mlp_dims = config['model']['mlp']['dims']
        self.dropout = config['model']['mlp']['dropout']
        self.seed = config['seed']
        self.weight_decay = config['weight_decay']
        self.epoch = config['epoch']
        self.save_param_dir = config['save_param_dir']
        self.dataset = config['dataset']
        self.skip_final_test = config.get('skip_final_test', False)
        self.selector_mode = config.get('selector_mode', 'panda_gumbel')
        self.reliability_signal = config.get('reliability_signal', 'branch_fusion')
        self.reliability_lambda = config.get('reliability_lambda', 0.05)
        self.reliability_gating = config.get('reliability_gating', 'distance')
        self.reliability_stats_mode = config.get('reliability_stats_mode', 'online')
        self.reliability_ema_momentum = config.get('reliability_ema_momentum', 0.9)
        self.selection_margin_lambda = config.get('selection_margin_lambda', 0.0)
        self.selection_margin = config.get('selection_margin', 0.1)
        self.aux_loss_weight = config.get('aux_loss_weight', 1.0)
        self.aux_text_weight = config.get('aux_text_weight', None)
        self.aux_image_weight = config.get('aux_image_weight', None)
        self.aux_fusion_weight = config.get('aux_fusion_weight', None)
        self.aux_schedule = config.get('aux_schedule', 'constant')
        self.aux_schedule_start = config.get('aux_schedule_start', 1.0)
        self.aux_schedule_end = config.get('aux_schedule_end', 1.0)
        self.aux_label_mode = config.get('aux_label_mode', 'true')
        self.aux_label_seed = config.get('aux_label_seed', None)
        self.aux_random_label_seed = config.get('aux_random_label_seed', None)
        self.aux_shuffle_seed = config.get('aux_shuffle_seed', None)
        self.aux_detach_features = config.get('aux_detach_features', False)
        self.r5a_grad_mode = config.get('r5a_grad_mode', 'none')
        self.r5a_log_dir = config.get('r5a_log_dir', None)
        self.r5a_log_interval = config.get('r5a_log_interval', 1)
        self.uea_aux_mode = config.get('uea_aux_mode', 'none')
        self.uea_utility_csv = config.get('uea_utility_csv', None)
        self.uea_alpha_max = config.get('uea_alpha_max', 0.5)
        self.uea_weight_floor = config.get('uea_weight_floor', 1e-8)
        self.uea_seed = config.get('uea_seed', self.seed)
        self.uea_boundary_low_margin_quantile = config.get('uea_boundary_low_margin_quantile', 0.25)
        self.uea_boundary_risk_quantile = config.get('uea_boundary_risk_quantile', 0.75)
        self.regret_lambda = config.get('regret_lambda', 0.0)
        self.route_balance_lambda = config.get('route_balance_lambda', 0.0)
        self.regret_margin = config.get('regret_margin', 0.0)
        self.router_tau_start = config.get('router_tau_start', 2.0)
        self.router_tau_end = config.get('router_tau_end', 1.0)
        self.adapter_dim = config.get('adapter_dim', 64)
        self.router_hidden = config.get('router_hidden', 128)
        if config['dataset']=="weibo":
            self.dataset_type = "CN"
            self.root_path = './Weibo/'
            self.train_path = self.root_path + 'train_origin.csv'  # 如果9个领域就要改成train.csv
            self.val_path = self.root_path + 'val_origin.csv'  # 如果9个领域就要改成val.csv
            self.test_path = self.root_path + 'test_origin.csv'  # 如果9个领域就要改成test.csv
            self.category_dict = {
                "经济": 0,
                "健康": 1,
                "军事": 2,
                "科学": 3,
                "政治": 4,
                "国际": 5,
                "教育": 6,
                "娱乐": 7,
                "社会": 8
            }
        if config['dataset']=="weibo21":
            self.dataset_type = "CN"
            self.root_path = './Weibo_21/'
            self.train_path = self.root_path + 'train_datasets.xlsx'#weibo21
            self.val_path = self.root_path + 'val_datasets.xlsx'#weibo21
            self.test_path = self.root_path + 'test_datasets.xlsx'#weibo21
            self.category_dict = {
                "科技": 0,
                "军事": 1,
                "教育考试": 2,
                "灾难事故": 3,
                "政治": 4,
                "医药健康": 5,
                "财经商业": 6,
                "文体娱乐": 7,
                "社会生活": 8
            }
        if config['dataset'] == "pheme":
            self.root_path = './pheme/'
            self.train_path = self.root_path + 'train.csv'#weibo21
            self.val_path = self.root_path + 'val.csv'#weibo21
            self.test_path = self.root_path + 'test.csv'#weibo21
            self.category_dict = {
                "society": 0,
                "military": 1,
                "international": 2,
                "entertainment": 3,
                "politics": 4
            }
        if config['dataset']=="FINE":
            self.dataset_type = "EN"
            self.root_path = './FINE/'
            self.train_path = self.root_path + 'FineFake_train.pkl'#weibo21
            self.val_path = self.root_path + 'FineFake_val.pkl'#weibo21
            self.test_path = self.root_path + 'FineFake_test.pkl'#weibo21
            self.category_dict = {
                "Society": 0,
                "Conflict": 1,
                "Politics": 2,
                "Entertainment": 3,
                "Health": 4,
                "Business": 5,
                "Uncategorized": 6
            }
    def get_dataloader(self,dataset):
        if self.emb_type == 'bert':
            if dataset =="weibo":
                loader = weibo_data(max_len=self.max_len, batch_size=self.batchsize, vocab_file=self.vocab_file,
                              category_dict=self.category_dict, num_workers=self.num_workers)
            if dataset =="weibo21":
                loader = weibo21_data(max_len=self.max_len, batch_size=self.batchsize, vocab_file=self.vocab_file,
                              category_dict=self.category_dict, num_workers=self.num_workers)
            if dataset =="pheme":
                loader = pheme_data(max_len=self.max_len, batch_size=self.batchsize, vocab_file=self.vocab_file,
                              category_dict=self.category_dict, num_workers=self.num_workers)
            if dataset =="FINE":
                loader = FINE_data(max_len=self.max_len, batch_size=self.batchsize, vocab_file=self.vocab_file,
                              category_dict=self.category_dict, num_workers=self.num_workers)
        #clip_weibo
        if dataset =="weibo":
            train_loader = loader.load_data(self.train_path,'Weibo/train_loader.pkl','Weibo/train_clip_loader.pkl',True)
            val_loader = loader.load_data(self.val_path,'Weibo/val_loader.pkl','Weibo/val_clip_loader.pkl',False)
            test_loader = loader.load_data(self.test_path,'Weibo/test_loader.pkl','Weibo/test_clip_loader.pkl',False)
        # clip_weibo21
        if dataset =="weibo21":
            val_loader = loader.load_data(self.val_path, 'Weibo_21/val_loader.pkl', 'Weibo_21/val_clip_loader.pkl', False)
            test_loader = loader.load_data(self.test_path, 'Weibo_21/test_loader.pkl', 'Weibo_21/test_clip_loader.pkl', False)
            train_loader = loader.load_data(self.train_path, 'Weibo_21/train_loader.pkl', 'Weibo_21/train_clip_loader.pkl', True)
        if dataset =="pheme":
            train_loader = loader.load_data(self.train_path, 'pheme/train_loader.pkl', 'pheme/train_clip_loader.pkl', True)
            val_loader = loader.load_data(self.val_path, 'pheme/val_loader.pkl', 'pheme/val_clip_loader.pkl', True)
            test_loader = loader.load_data(self.test_path, 'pheme/test_loader.pkl', 'pheme/test_clip_loader.pkl', True)
        if dataset =="FINE":
            train_loader = loader.load_data(self.train_path, 'FINE/train_loader.pkl', 'FINE/train_clip_loader.pkl', True)
            val_loader = loader.load_data(self.val_path, 'FINE/val_loader.pkl', 'FINE/val_clip_loader.pkl', True)
            test_loader = loader.load_data(self.test_path, 'FINE/test_loader.pkl', 'FINE/test_clip_loader.pkl', True)
        return train_loader, val_loader, test_loader

    def config2dict(self):
        config_dict = {}
        for k, v in self.configinfo.items():
            config_dict[k] = v
        return config_dict

    def main(self):
        train_loader, val_loader, test_loader = self.get_dataloader(self.dataset)
        if self.model_name == 'FTmodel':
            trainer = LPROMPTIMAGETrainer(emb_dim=self.emb_dim, mlp_dims=self.mlp_dims, bert=self.bert,
                                    use_cuda=self.use_cuda, lr=self.lr, train_loader=train_loader, dropout=self.dropout,
                                    weight_decay=self.weight_decay, val_loader=val_loader, test_loader=test_loader,
                                    category_dict=self.category_dict, early_stop=self.early_stop, epoches=self.epoch,
                                    save_param_dir=os.path.join(self.save_param_dir, self.model_name),dataset_type=self.dataset_type,
                                    skip_final_test=self.skip_final_test,
                                    selector_mode=self.selector_mode, reliability_signal=self.reliability_signal,
                                    reliability_lambda=self.reliability_lambda,
                                    reliability_gating=self.reliability_gating,
                                    reliability_stats_mode=self.reliability_stats_mode,
                                    reliability_ema_momentum=self.reliability_ema_momentum,
                                    selection_margin_lambda=self.selection_margin_lambda,
                                    selection_margin=self.selection_margin,
                                    aux_loss_weight=self.aux_loss_weight,
                                    aux_text_weight=self.aux_text_weight,
                                    aux_image_weight=self.aux_image_weight,
                                    aux_fusion_weight=self.aux_fusion_weight,
                                    aux_schedule=self.aux_schedule,
                                    aux_schedule_start=self.aux_schedule_start,
                                    aux_schedule_end=self.aux_schedule_end,
                                    aux_label_mode=self.aux_label_mode,
                                    aux_label_seed=self.aux_label_seed,
                                    aux_random_label_seed=self.aux_random_label_seed,
                                    aux_shuffle_seed=self.aux_shuffle_seed,
                                    aux_detach_features=self.aux_detach_features,
                                    r5a_grad_mode=self.r5a_grad_mode,
                                    r5a_log_dir=self.r5a_log_dir,
                                    r5a_log_interval=self.r5a_log_interval,
                                    uea_aux_mode=self.uea_aux_mode,
                                    uea_utility_csv=self.uea_utility_csv,
                                    uea_alpha_max=self.uea_alpha_max,
                                    uea_weight_floor=self.uea_weight_floor,
                                    uea_seed=self.uea_seed,
                                    uea_boundary_low_margin_quantile=self.uea_boundary_low_margin_quantile,
                                    uea_boundary_risk_quantile=self.uea_boundary_risk_quantile,
                                    regret_lambda=self.regret_lambda,
                                    route_balance_lambda=self.route_balance_lambda,
                                    regret_margin=self.regret_margin,
                                    router_tau_start=self.router_tau_start,
                                    router_tau_end=self.router_tau_end,
                                    adapter_dim=self.adapter_dim,
                                    router_hidden=self.router_hidden)
        if self.model_name == 'FTmodel2':
            trainer = LPROMPTIMAGETrainer2(emb_dim=self.emb_dim, mlp_dims=self.mlp_dims, bert=self.bert,
                                    use_cuda=self.use_cuda, lr=self.lr, train_loader=train_loader, dropout=self.dropout,
                                    weight_decay=self.weight_decay, val_loader=val_loader, test_loader=test_loader,
                                    category_dict=self.category_dict, early_stop=self.early_stop, epoches=self.epoch,
                                    save_param_dir=os.path.join(self.save_param_dir, self.model_name),dataset_type=self.dataset_type)
        if self.model_name == 'clean_vib':
            trainer = LPROMPTIMAGETrainer3(emb_dim=self.emb_dim, mlp_dims=self.mlp_dims, bert=self.bert,
                                    use_cuda=self.use_cuda, lr=self.lr, train_loader=train_loader, dropout=self.dropout,
                                    weight_decay=self.weight_decay, val_loader=val_loader, test_loader=test_loader,
                                    category_dict=self.category_dict, early_stop=self.early_stop, epoches=self.epoch,
                                    save_param_dir=os.path.join(self.save_param_dir, self.model_name),dataset_type=self.dataset_type)
        trainer.train()
