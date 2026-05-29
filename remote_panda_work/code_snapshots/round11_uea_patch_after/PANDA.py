import csv
import os
import tqdm
import torch
import numpy as np
from positional_encodings.torch_encodings import PositionalEncoding1D, PositionalEncoding2D, PositionalEncodingPermute3D
from transformers import BertModel
import torch.nn as nn
import torch.nn.functional as F
# from positional_encodings.torch_encodings import PositionalEncoding1D
import models_mae
from utils.utils import data2gpu, Averager, metrics, Recorder, clipdata2gpu
from utils.utils import metricsTrueFalse
from .layers import *
from .pivot import *
from timm.models.vision_transformer import Block
import cn_clip.clip as clip
from cn_clip.clip import load_from_name, available_models
import math


class SimpleGate(nn.Module):
    def __init__(self, dim=1):
        super(SimpleGate, self).__init__()
        self.dim = dim

    def forward(self, x):
        x1, x2 = x.chunk(2, dim=self.dim)
        return x1 * x2

class AdaIN(nn.Module):
    def __init__(self):
        super().__init__()

    def mu(self, x):
        return torch.sum(x,(1))/(x.shape[1])

    def sigma(self, x):
        return torch.sqrt((torch.sum((x.permute([1,0])-self.mu(x)).permute([1,0])**2,(1))+0.000000023)/(x.shape[1]))

    def forward(self, x, mu, sigma):
        # print(mu.shape) # 12
        x_mean = self.mu(x)
        x_std = self.sigma(x)
        x_reduce_mean = x.permute([1, 0]) - x_mean
        x_norm = x_reduce_mean/x_std
        # print(x_mean.shape) # 768, 12
        return (sigma.squeeze(1)*(x_norm + mu.squeeze(1))).permute([1,0])


class DomainCollaborativeAttention(nn.Module):
    """
    Domain-Collaborative Attention (DCA) module.
    Fuses knowledge from selected neighbor domains using cross-attention.
    The target domain's prompts act as Query, and prompts from the neighbor
    domains serve as Key and Value.
    """
    def __init__(self, d_model, nhead, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.W_Q = nn.Linear(d_model, d_model, bias=False)
        self.W_K = nn.Linear(d_model, d_model, bias=False)
        self.W_V = nn.Linear(d_model, d_model, bias=False)
        self.dropout = nn.Dropout(dropout)
        self.out_proj = nn.Linear(d_model, d_model)

    def forward(self, query, key, value, key_padding_mask=None):
        """
        Args:
            query (Tensor): Target domain prompts (Batch, L_q, D_p)
            key (Tensor): Neighbor domain prompts (Batch, L_k, D_p)
            value (Tensor): Neighbor domain prompts (Batch, L_k, D_p)
            key_padding_mask (Tensor): Mask for non-selected domains (Batch, L_k)
        Returns:
            Tensor: Collaborated knowledge vector (Batch, L_q, D_p)
        """
        Q = self.W_Q(query)
        K = self.W_K(key)
        V = self.W_V(value)

        # Reshape for multi-head attention
        batch_size = Q.size(0)
        Q = Q.view(batch_size, -1, self.nhead, self.d_model // self.nhead).transpose(1, 2)
        K = K.view(batch_size, -1, self.nhead, self.d_model // self.nhead).transpose(1, 2)
        V = V.view(batch_size, -1, self.nhead, self.d_model // self.nhead).transpose(1, 2)

        attn_scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(Q.size(-1))

        if key_padding_mask is not None:
            # Expand mask for multi-head attention
            mask = key_padding_mask.unsqueeze(1).unsqueeze(2) # (Batch, 1, 1, L_k)
            attn_scores = attn_scores.masked_fill(mask == 0, float('-inf'))

        attn_probs = F.softmax(attn_scores, dim=-1)
        attn_probs = self.dropout(attn_probs)

        context = torch.matmul(attn_probs, V)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)

        return self.out_proj(context)



class MultiDomainPLEFENDModel(torch.nn.Module):
    def __init__(
            self,
            emb_dim,
            mlp_dims,
            bert,
            out_channels,
            dropout,
            domain_num=9,
            selector_mode='panda_gumbel',
            reliability_signal='branch_fusion',
            reliability_lambda=0.05,
            reliability_gating='distance',
            reliability_stats_mode='online',
            reliability_ema_momentum=0.9,
            selection_margin_lambda=0.0,
            selection_margin=0.1,
            regret_lambda=0.0,
            route_balance_lambda=0.0,
            regret_margin=0.0,
            router_tau_start=2.0,
            router_tau_end=1.0,
            adapter_dim=64,
            router_hidden=128,
            aux_detach_features=False):
        super(MultiDomainPLEFENDModel, self).__init__()
        self.num_expert = 6
        self.task_num = 2
        # self.domain_num = 9
        # Per user request, the original domain_num is confusing, so we use a clear parameter
        self.domain_num = domain_num
        self.gate_num = 3
        self.num_share = 1
        self.unified_dim, self.text_dim = emb_dim, 768
        self.image_dim = 768
        self.bert = BertModel.from_pretrained(bert).requires_grad_(False)
        feature_kernel = {1: 64, 2: 64, 3: 64, 5: 64, 10: 64}
        self.text_token_len = 197
        self.image_token_len = 197

        # ==================== Existing Expert Networks (No Changes) ====================
        text_expert_list = []
        for i in range(self.task_num): # Use task_num for compatibility with original code structure
            text_expert = []
            for j in range(self.num_expert):
                text_expert.append(cnn_extractor(emb_dim, feature_kernel))
            text_expert = nn.ModuleList(text_expert)
            text_expert_list.append(text_expert)
        self.text_experts = nn.ModuleList(text_expert_list)

        image_expert_list = []
        for i in range(self.task_num):
            image_expert = []
            for j in range(self.num_expert):
                image_expert.append(cnn_extractor(self.image_dim, feature_kernel))
            image_expert = nn.ModuleList(image_expert)
            image_expert_list.append(image_expert)
        self.image_experts = nn.ModuleList(image_expert_list)

        fusion_expert_list = []
        for i in range(self.task_num):
            fusion_expert = []
            for j in range(self.num_expert):
                expert = nn.Sequential(nn.Linear(320, 320), nn.SiLU(), nn.Linear(320, 320))
                fusion_expert.append(expert)
            fusion_expert = nn.ModuleList(fusion_expert)
            fusion_expert_list.append(fusion_expert)
        self.fusion_experts = nn.ModuleList(fusion_expert_list)

        final_expert_list = []
        for i in range(self.task_num):
            final_expert = []
            for j in range(self.num_expert):
                final_expert.append(Block(dim=320, num_heads=8))
            final_expert = nn.ModuleList(final_expert)
            final_expert_list.append(final_expert)
        self.final_experts = nn.ModuleList(final_expert_list)

        text_share_expert, image_share_expert, fusion_share_expert,final_share_expert = [], [], [],[]
        for i in range(self.num_share):
            text_share, image_share, fusion_share, final_share = [], [], [], []
            for j in range(self.num_expert*2):
                text_share.append(cnn_extractor(emb_dim, feature_kernel))
                image_share.append(cnn_extractor(self.image_dim, feature_kernel))
                expert = nn.Sequential(nn.Linear(320, 320), nn.SiLU(), nn.Linear(320, 320))
                fusion_share.append(expert)
                final_share.append(Block(dim=320, num_heads=8))
            text_share_expert.append(nn.ModuleList(text_share))
            image_share_expert.append(nn.ModuleList(image_share))
            fusion_share_expert.append(nn.ModuleList(fusion_share))
            final_share_expert.append(nn.ModuleList(final_share))
        self.text_share_expert = nn.ModuleList(text_share_expert)
        self.image_share_expert = nn.ModuleList(image_share_expert)
        self.fusion_share_expert = nn.ModuleList(fusion_share_expert)
        self.final_share_expert = nn.ModuleList(final_share_expert)

        image_gate_list, text_gate_list, fusion_gate_list, fusion_gate_list0,final_gate_list = [], [], [], [],[]
        for i in range(self.task_num):
            image_gate_list.append(nn.Sequential(nn.Linear(self.unified_dim, self.unified_dim), nn.SiLU(), nn.Linear(self.unified_dim, self.num_expert * 3), nn.Dropout(0.1), nn.Softmax(dim=1)))
            text_gate_list.append(nn.Sequential(nn.Linear(self.unified_dim, self.unified_dim), nn.SiLU(), nn.Linear(self.unified_dim, self.num_expert * 3), nn.Dropout(0.1), nn.Softmax(dim=1)))
            fusion_gate_list.append(nn.Sequential(nn.Linear(self.unified_dim, self.unified_dim), nn.SiLU(), nn.Linear(self.unified_dim, self.num_expert * 4), nn.Dropout(0.1), nn.Softmax(dim=1)))
            fusion_gate_list0.append(nn.Sequential(nn.Linear(320, 160), nn.SiLU(), nn.Linear(160, self.num_expert * 3), nn.Dropout(0.1), nn.Softmax(dim=1)))
            final_gate_list.append(nn.Sequential(nn.Linear(320, 320), nn.SiLU(), nn.Linear(320, 160), nn.SiLU(), nn.Linear(160, self.num_expert * 3), nn.Dropout(0.1), nn.Softmax(dim=1)))
        self.image_gate_list = nn.ModuleList(image_gate_list)
        self.text_gate_list = nn.ModuleList(text_gate_list)
        self.fusion_gate_list = nn.ModuleList(fusion_gate_list)
        self.fusion_gate_list0 = nn.ModuleList(fusion_gate_list0)
        self.final_gate_list = nn.ModuleList(final_gate_list)

        self.text_attention = MaskAttention(self.unified_dim)
        self.image_attention = TokenAttention(self.unified_dim)
        self.fusion_attention = TokenAttention(self.unified_dim * 2)
        self.final_attention = TokenAttention(320)

        # ==================== Existing Classifiers for Auxiliary Tasks (No Changes) ====================
        self.text_classifier = MLP(320, mlp_dims, dropout)
        self.image_classifier = MLP(320, mlp_dims, dropout)
        self.fusion_classifier = MLP(320, mlp_dims, dropout)

        # self.max_classifier will be replaced by PANDA's final classification head
        # self.max_classifier = MLP(320 * 1, mlp_dims, dropout)

        self.MLP_fusion = MLP_fusion(960, 320, [348], 0.1)
        self.domain_fusion = MLP_fusion(320, 320, [348], 0.1)
        self.MLP_fusion0 = MLP_fusion(768 * 2, 768, [348], 0.1)
        self.clip_fusion = clip_fuion(1024, 320, [348], 0.1)
        self.att_mlp_text = MLP_fusion(320, 2, [174], 0.1)
        self.att_mlp_img = MLP_fusion(320, 2, [174], 0.1)
        self.att_mlp_mm = MLP_fusion(320, 2, [174], 0.1)

        self.model_size = "base"
        self.image_model = models_mae.__dict__["mae_vit_{}_patch16".format(self.model_size)](norm_pix_loss=False)
        self.image_model.cuda()
        checkpoint = torch.load('./mae_pretrain_vit_{}.pth'.format(self.model_size), map_location='cpu')
        self.image_model.load_state_dict(checkpoint['model'], strict=False)
        for param in self.image_model.parameters():
            param.requires_grad = False

        # ==================== Existing Graph/Pivot/Transformer parts  ====================
        self.ClipModel,_ = load_from_name("ViT-B-16", device="cuda", download_root='./')
        feature_emb_size, img_emb_size, text_emb_size = 320, 320, 320
        feature_num = 4
        self.layers = 12
        self.transformers = torch.nn.ModuleList([TransformerLayer(feature_emb_size, head_num=4, dropout=0.6) for _ in range(self.layers)])

        self.mlp_img = torch.nn.ModuleList([MLP_trans(img_emb_size, feature_emb_size, dropout=0.6) for _ in range(feature_num)])
        self.mlp_text = torch.nn.ModuleList([MLP_trans(text_emb_size, feature_emb_size, dropout=0.6) for _ in range(feature_num)])


        # PANDA Hyperparameters
        self.p_Lp = 4  # Number of prompts per modality view
        self.p_Dp = 320 # Dimension of prompt vectors, matching feature dim
        self.p_M = 16  # Number of prototypes per domain
        self.p_S = 2   # Number of top-S neighbor domains to select
        self.selector_mode = 'panda_gumbel' if selector_mode == 'gumbel' else selector_mode
        self.reliability_signal = reliability_signal
        self.reliability_lambda = reliability_lambda
        self.reliability_gating = reliability_gating
        self.reliability_stats_mode = reliability_stats_mode
        self.reliability_ema_momentum = reliability_ema_momentum
        self.selection_margin_lambda = selection_margin_lambda
        self.selection_margin = selection_margin
        self.regret_lambda = regret_lambda
        self.route_balance_lambda = route_balance_lambda
        self.regret_margin = regret_margin
        self.router_tau_start = router_tau_start
        self.router_tau_end = router_tau_end
        self.router_tau = router_tau_start
        self.adapter_dim = adapter_dim
        self.router_hidden = router_hidden
        self.aux_detach_features = aux_detach_features
        self.register_buffer('reliability_domain_sum', torch.zeros(self.domain_num), persistent=False)
        self.register_buffer('reliability_domain_sq_sum', torch.zeros(self.domain_num), persistent=False)
        self.register_buffer('reliability_domain_count', torch.zeros(self.domain_num), persistent=False)
        self._current_reliability_score = None
        self._last_neighbor_diag = {}
        self._selection_margin_loss = None
        self._r3_regret_loss = None
        self._r3_balance_loss = None
        self.collect_reliability_stats = False

        # 2.2 Domain-aware Modal Prompt Generation (DMPG)
        # Prompts for text, vision, and multimodal views are concatenated
        self.domain_modal_prompts = nn.Parameter(torch.randn(self.domain_num, 3 * self.p_Lp, self.p_Dp))

        # 2.3 Prototype-based Asymmetric Distance (PAD)
        # 2.3.1 Domain Prototype Learning
        self.domain_prototypes = nn.Parameter(torch.randn(self.domain_num, self.p_M, 320))
        # Autoencoder for prototype learning
        self.proto_encoder = nn.Sequential(nn.Linear(320, 320), nn.ReLU(), nn.Linear(320, 320))
        self.proto_decoder = nn.Sequential(nn.Linear(320, 320), nn.ReLU(), nn.Linear(320, 320))

        # 2.4 Dynamic Neighbor-Domain Selection and Fusion
        # 2.4.2 Domain-Collaborative Attention (DCA)
        self.dca_module = DomainCollaborativeAttention(d_model=self.p_Dp, nhead=8, dropout=0.1)

        # 2.5 Prediction and Loss Function
        # 2.5.1 Final Classification Head
        self.final_classifier_panda = MLP(320 + self.p_Dp, mlp_dims, dropout) # h_di (320) + h_collab (Dp)

        # R3-PANDA lightweight source-utility router components are only
        # registered for regret_soft modes to keep old checkpoints compatible.
        self.r3_domain_emb_dim = 32
        self.r3_reliability_dim = 3
        if self._is_r3_mode():
            self.r3_domain_embeddings = nn.Embedding(self.domain_num, self.r3_domain_emb_dim)
            router_input_dim = 320 + self.r3_domain_emb_dim * 2 + self.r3_reliability_dim
            self.r3_router_mlp = nn.Sequential(
                nn.Linear(router_input_dim, self.router_hidden),
                nn.SiLU(),
                nn.Linear(self.router_hidden, 1)
            )
            self.r3_source_adapters = nn.ModuleList([
                nn.Sequential(
                    nn.Linear(320, self.adapter_dim),
                    nn.SiLU(),
                    nn.Linear(self.adapter_dim, 320)
                )
                for _ in range(self.domain_num)
            ])
        else:
            self.r3_domain_embeddings = None
            self.r3_router_mlp = None
            self.r3_source_adapters = None



    def _calculate_pad(self):
        """
        Helper function to calculate Prototype-based Asymmetric Distance (PAD) matrix.
        dist(s->t) measures how well source domain s's prototypes fit into target domain t.
        """
        protos = self.domain_prototypes # (D, M, Dim)
        # Expand dims for broadcasting: protos1 -> (D, 1, M, Dim), protos2 -> (1, D, M, Dim)
        protos1 = protos.unsqueeze(1)
        protos2 = protos.unsqueeze(0)

        # Calculate pairwise L2 distance between all prototypes of all domains
        # Shape: (D_s, D_t, M_s, M_t)
        pairwise_dist = torch.cdist(protos1, protos2, p=2.0)

        # For each source prototype, find the min distance to any target prototype
        # Shape: (D_s, D_t, M_s)
        min_dist_to_target, _ = torch.min(pairwise_dist, dim=3)

        # Average these minimum distances over all source prototypes
        # This yields the asymmetric distance dist(s->t)
        # Shape: (D_s, D_t)
        asymmetric_dist_matrix = torch.mean(min_dist_to_target, dim=2)

        return asymmetric_dist_matrix

    def _reliability_score(self, text_pred, image_pred, fusion_pred, clip_image_feature=None, clip_text_feature=None):
        branch_disagreement = torch.abs(text_pred - image_pred)
        fusion_uncertainty = 1.0 - torch.abs(2.0 * fusion_pred - 1.0)
        aux_mean_pred = (text_pred + image_pred + fusion_pred) / 3.0
        confidence_uncertainty = 1.0 - torch.abs(2.0 * aux_mean_pred - 1.0)
        overconfidence = torch.abs(2.0 * aux_mean_pred - 1.0)
        clip_dissimilarity = None
        if clip_image_feature is not None and clip_text_feature is not None:
            clip_cos = torch.sum(clip_image_feature * clip_text_feature, dim=-1)
            clip_dissimilarity = (1.0 - clip_cos) / 2.0
        if self.reliability_signal == 'branch':
            score = branch_disagreement
        elif self.reliability_signal == 'fusion':
            score = fusion_uncertainty
        elif self.reliability_signal in ['clip', 'clip_dissimilarity']:
            if clip_dissimilarity is None:
                raise ValueError('clip reliability signal requires CLIP image/text features')
            score = clip_dissimilarity
        elif self.reliability_signal == 'branch_fusion_clip':
            if clip_dissimilarity is None:
                raise ValueError('branch_fusion_clip reliability signal requires CLIP image/text features')
            score = (branch_disagreement + fusion_uncertainty + clip_dissimilarity) / 3.0
        elif self.reliability_signal == 'confidence_uncertainty':
            score = confidence_uncertainty
        elif self.reliability_signal == 'overconfidence':
            score = overconfidence
        elif self.reliability_signal == 'random':
            score = torch.rand_like(fusion_pred)
        else:
            score = 0.5 * (branch_disagreement + fusion_uncertainty)
        return score.detach().clamp(0.0, 1.0)

    def _reliability_vector(self, text_pred, image_pred, fusion_pred, clip_image_feature=None, clip_text_feature=None):
        branch_disagreement = torch.abs(text_pred - image_pred)
        fusion_uncertainty = 1.0 - torch.abs(2.0 * fusion_pred - 1.0)
        aux_mean_pred = (text_pred + image_pred + fusion_pred) / 3.0
        confidence_uncertainty = 1.0 - torch.abs(2.0 * aux_mean_pred - 1.0)
        overconfidence = torch.abs(2.0 * aux_mean_pred - 1.0)
        zeros = torch.zeros_like(branch_disagreement)
        if clip_image_feature is not None and clip_text_feature is not None:
            clip_cos = torch.sum(clip_image_feature * clip_text_feature, dim=-1)
            clip_dissimilarity = (1.0 - clip_cos) / 2.0
        else:
            clip_dissimilarity = zeros

        if self.reliability_signal == 'branch':
            vec = torch.stack([branch_disagreement, zeros, zeros], dim=1)
        elif self.reliability_signal == 'fusion':
            vec = torch.stack([zeros, fusion_uncertainty, zeros], dim=1)
        elif self.reliability_signal == 'confidence_uncertainty':
            vec = torch.stack([zeros, zeros, confidence_uncertainty], dim=1)
        elif self.reliability_signal == 'overconfidence':
            vec = torch.stack([overconfidence, overconfidence, overconfidence], dim=1)
        elif self.reliability_signal == 'random':
            random_score = torch.rand_like(branch_disagreement)
            vec = torch.stack([random_score, random_score, random_score], dim=1)
        elif self.reliability_signal in ['clip', 'clip_dissimilarity']:
            vec = torch.stack([clip_dissimilarity, clip_dissimilarity, clip_dissimilarity], dim=1)
        elif self.reliability_signal == 'branch_fusion_clip':
            vec = torch.stack([branch_disagreement, fusion_uncertainty, clip_dissimilarity], dim=1)
        else:
            vec = torch.stack([branch_disagreement, fusion_uncertainty, confidence_uncertainty], dim=1)
        return vec.detach().clamp(0.0, 1.0)

    def _is_r3_mode(self):
        return str(self.selector_mode).startswith('regret_soft')

    def _r3_uses_adapter(self):
        return self._is_r3_mode() and ('adapter' in str(self.selector_mode))

    def _r3_uses_regret(self):
        return self._is_r3_mode() and ('neg' in str(self.selector_mode))

    def _r3_uses_reliability(self):
        return self._is_r3_mode() and ('reliability' in str(self.selector_mode))

    def _r3_uses_shuffled_regret(self):
        return self._is_r3_mode() and ('shuffled' in str(self.selector_mode))

    def set_regret_epoch(self, epoch_idx, total_epochs):
        denom = max(float(total_epochs - 1), 1.0)
        progress = min(max(float(epoch_idx) / denom, 0.0), 1.0)
        self.router_tau = self.router_tau_start + progress * (self.router_tau_end - self.router_tau_start)

    def reset_reliability_stats(self):
        self.reliability_domain_sum.zero_()
        self.reliability_domain_sq_sum.zero_()
        self.reliability_domain_count.zero_()

    def _update_reliability_domain_stats(self, domain_indices, reliability_score):
        if reliability_score is None:
            return
        if self.collect_reliability_stats:
            update_mode = 'accumulate'
        elif not self.training:
            return
        elif self.reliability_stats_mode == 'online':
            update_mode = 'accumulate'
        elif self.reliability_stats_mode == 'ema':
            update_mode = 'ema'
        else:
            return
        with torch.no_grad():
            for domain_idx in domain_indices.detach().unique():
                mask = domain_indices == domain_idx
                idx = int(domain_idx.item())
                domain_score = reliability_score[mask]
                if update_mode == 'ema':
                    batch_mean = domain_score.mean()
                    batch_sq_mean = (domain_score ** 2).mean()
                    if self.reliability_domain_count[idx] <= 0:
                        self.reliability_domain_sum[idx] = batch_mean
                        self.reliability_domain_sq_sum[idx] = batch_sq_mean
                    else:
                        momentum = float(self.reliability_ema_momentum)
                        self.reliability_domain_sum[idx] = momentum * self.reliability_domain_sum[idx] + (1.0 - momentum) * batch_mean
                        self.reliability_domain_sq_sum[idx] = momentum * self.reliability_domain_sq_sum[idx] + (1.0 - momentum) * batch_sq_mean
                    self.reliability_domain_count[idx] = 1.0
                else:
                    self.reliability_domain_sum[idx] += domain_score.sum()
                    self.reliability_domain_sq_sum[idx] += (domain_score ** 2).sum()
                    self.reliability_domain_count[idx] += mask.sum()

    def _reliability_domain_stats(self, fallback_score):
        counts = self.reliability_domain_count.to(fallback_score.device)
        sums = self.reliability_domain_sum.to(fallback_score.device)
        sq_sums = self.reliability_domain_sq_sum.to(fallback_score.device)
        fallback = fallback_score.detach().mean() if fallback_score is not None and fallback_score.numel() else torch.tensor(0.5, device=counts.device)
        means = sums / counts.clamp_min(1.0)
        means = torch.where(counts > 0, means, fallback.expand_as(means))
        sq_means = sq_sums / counts.clamp_min(1.0)
        sq_means = torch.where(counts > 0, sq_means, fallback.pow(2).expand_as(sq_means))
        vars_ = torch.clamp(sq_means - means.pow(2), min=1e-6)
        stds = torch.sqrt(vars_)
        total_count = counts.sum()
        if total_count > 0:
            global_mean = sums.sum() / total_count.clamp_min(1.0)
            global_sq_mean = sq_sums.sum() / total_count.clamp_min(1.0)
            global_std = torch.sqrt(torch.clamp(global_sq_mean - global_mean.pow(2), min=1e-6))
        else:
            global_mean = fallback
            global_std = torch.tensor(1.0, device=counts.device)
        return means, stds, global_mean, global_std

    def _build_neighbor_logits(self, sim_matrix, target_domain_indices, reliability_score=None):
        batch_sims = sim_matrix[:, target_domain_indices].transpose(0, 1)
        base_logits = torch.log(batch_sims + 1e-9)
        logits = base_logits
        reliability_adjustment = None
        reliability_domain_mean = None
        reliability_domain_std = None
        reliability_sample_z = None
        reliability_domain_z = None
        if self.selector_mode == 'reliability' and reliability_score is not None and self.reliability_lambda != 0:
            reliability_domain_mean, reliability_domain_std, global_mean, global_std = self._reliability_domain_stats(reliability_score)
            if self.reliability_gating == 'high_unc_penalty':
                reliability_sample_z = (reliability_score - global_mean) / global_std.clamp_min(1e-6)
                reliability_domain_z = (reliability_domain_mean - global_mean) / global_std.clamp_min(1e-6)
                reliability_adjustment = F.relu(reliability_sample_z).unsqueeze(1) * F.relu(reliability_domain_z).unsqueeze(0)
                logits = base_logits - self.reliability_lambda * reliability_adjustment
            elif self.reliability_gating == 'stable_source_reward':
                reliability_sample_z = (reliability_score - global_mean) / global_std.clamp_min(1e-6)
                reliability_domain_z = (reliability_domain_mean - global_mean) / global_std.clamp_min(1e-6)
                reliability_adjustment = F.relu(reliability_sample_z).unsqueeze(1) * F.relu(-reliability_domain_z).unsqueeze(0)
                logits = base_logits + self.reliability_lambda * reliability_adjustment
            else:
                reliability_adjustment = torch.abs(reliability_score.unsqueeze(1) - reliability_domain_mean.unsqueeze(0))
                logits = base_logits - self.reliability_lambda * reliability_adjustment
        return batch_sims, base_logits, logits, reliability_adjustment, reliability_domain_mean, reliability_domain_std, reliability_sample_z, reliability_domain_z

    def _gumbel_neighbor_selector(self, sim_matrix, target_domain_indices):
        """
        Gumbel-based Neighbor Selector (GNS) to select top-S neighbors.
        Uses Gumbel-top-k trick for differentiable selection.
        """
        reliability_score = self._current_reliability_score
        (
            batch_sims,
            base_logits,
            logits,
            reliability_adjustment,
            reliability_domain_mean,
            reliability_domain_std,
            reliability_sample_z,
            reliability_domain_z,
        ) = self._build_neighbor_logits(sim_matrix, target_domain_indices, reliability_score)

        if self.selector_mode == 'deterministic_train' or ((self.selector_mode in ['deterministic', 'reliability']) and not self.training):
            selector_scores = logits
        else:
            gumbel_noise = -torch.log(-torch.log(torch.rand_like(logits) + 1e-9) + 1e-9)
            selector_scores = logits + gumbel_noise

        # Select top-S neighbors based on perturbed scores
        top_values, top_indices = torch.topk(selector_scores, self.p_S, dim=1) # (Batch, S)
        deterministic_values, deterministic_topk = torch.topk(logits, self.p_S, dim=1)
        if logits.shape[1] >= 2:
            top2 = torch.topk(logits, 2, dim=1).values
            top1_top2_margin = top2[:, 0] - top2[:, 1]
        else:
            top1_top2_margin = torch.zeros(logits.shape[0], device=logits.device)
        if logits.shape[1] > self.p_S:
            boundary_values = torch.topk(logits, self.p_S + 1, dim=1).values
            selection_boundary_margin = boundary_values[:, self.p_S - 1] - boundary_values[:, self.p_S]
        else:
            selection_boundary_margin = top1_top2_margin
        self._selection_margin_loss = F.relu(self.selection_margin - selection_boundary_margin).mean()
        self._last_neighbor_diag = {
            'selector_mode': self.selector_mode,
            'reliability_signal': self.reliability_signal,
            'reliability_gating': self.reliability_gating,
            'reliability_stats_mode': self.reliability_stats_mode,
            'pad_similarity': batch_sims.detach(),
            'base_neighbor_logits': base_logits.detach(),
            'neighbor_logits': logits.detach(),
            'selector_scores': selector_scores.detach(),
            'selected_neighbor_logits': top_values.detach(),
            'selected_neighbors': top_indices.detach(),
            'deterministic_topk': deterministic_topk.detach(),
            'deterministic_topk_logits': deterministic_values.detach(),
            'top1_top2_margin': top1_top2_margin.detach(),
            'selection_boundary_margin': selection_boundary_margin.detach(),
        }
        if reliability_score is not None:
            self._last_neighbor_diag['reliability_score'] = reliability_score.detach()
        if reliability_adjustment is not None:
            self._last_neighbor_diag['reliability_adjustment'] = reliability_adjustment.detach()
        if reliability_domain_mean is not None:
            self._last_neighbor_diag['reliability_domain_mean'] = reliability_domain_mean.detach()
        if reliability_domain_std is not None:
            self._last_neighbor_diag['reliability_domain_std'] = reliability_domain_std.detach()
        if reliability_sample_z is not None:
            self._last_neighbor_diag['reliability_sample_z'] = reliability_sample_z.detach()
        if reliability_domain_z is not None:
            self._last_neighbor_diag['reliability_domain_z'] = reliability_domain_z.detach()

        return top_indices

    def selection_margin_loss(self):
        if self._selection_margin_loss is None:
            return None
        return self._selection_margin_loss

    def r3_losses(self):
        return self._r3_regret_loss, self._r3_balance_loss

    def _run_r3_regret_soft_router(self, h_di, target_prompts, sim_matrix, domain_indices, reliability_vector, label=None):
        batch_size = h_di.size(0)
        device = h_di.device
        domain_ids = torch.arange(self.domain_num, device=device)
        batch_sims = sim_matrix[:, domain_indices].transpose(0, 1)
        base_logits = torch.log(batch_sims + 1e-9)

        if self.selector_mode == 'regret_soft_pad_only':
            router_delta = torch.zeros_like(base_logits)
        else:
            target_emb = self.r3_domain_embeddings(domain_indices)
            source_emb = self.r3_domain_embeddings(domain_ids)
            h_expand = h_di.unsqueeze(1).expand(-1, self.domain_num, -1)
            target_expand = target_emb.unsqueeze(1).expand(-1, self.domain_num, -1)
            source_expand = source_emb.unsqueeze(0).expand(batch_size, -1, -1)
            if self._r3_uses_reliability():
                rel_vec = reliability_vector
            else:
                rel_vec = torch.zeros(batch_size, self.r3_reliability_dim, device=device)
            rel_expand = rel_vec.unsqueeze(1).expand(-1, self.domain_num, -1)
            router_input = torch.cat([h_expand, target_expand, source_expand, rel_expand], dim=-1)
            router_delta = self.r3_router_mlp(router_input.reshape(batch_size * self.domain_num, -1)).view(batch_size, self.domain_num)

        router_logits = base_logits + router_delta
        tau = max(float(self.router_tau), 1e-4)
        alpha = F.softmax(router_logits / tau, dim=1)

        source_prompts = self.domain_modal_prompts.unsqueeze(0).expand(batch_size, -1, -1, -1)
        query = target_prompts.unsqueeze(1).expand(-1, self.domain_num, -1, -1).reshape(
            batch_size * self.domain_num, 3 * self.p_Lp, self.p_Dp)
        key_value = source_prompts.reshape(batch_size * self.domain_num, 3 * self.p_Lp, self.p_Dp)
        key_padding_mask = torch.ones(batch_size * self.domain_num, 3 * self.p_Lp, device=device)
        collaborated_prompts = self.dca_module(query, key_value, key_value, key_padding_mask)
        source_collab = torch.mean(collaborated_prompts, dim=1).view(batch_size, self.domain_num, self.p_Dp)

        if self._r3_uses_adapter():
            adapter_outputs = torch.stack([adapter(h_di) for adapter in self.r3_source_adapters], dim=1)
        else:
            adapter_outputs = torch.zeros(batch_size, self.domain_num, h_di.size(1), device=device)

        candidate_h = h_di.unsqueeze(1) + adapter_outputs
        candidate_final = torch.cat([candidate_h, source_collab], dim=-1)
        candidate_logits = self.final_classifier_panda(
            candidate_final.reshape(batch_size * self.domain_num, -1)).view(batch_size, self.domain_num)

        h_route = h_di + torch.sum(alpha.unsqueeze(-1) * adapter_outputs, dim=1)
        h_collab = torch.sum(alpha.unsqueeze(-1) * source_collab, dim=1)
        fake_news_logits = self.final_classifier_panda(torch.cat([h_route, h_collab], dim=1)).squeeze(1)

        entropy = -(alpha * torch.log(alpha.clamp_min(1e-9))).sum(dim=1)
        effective_source_num = torch.exp(entropy)
        self_route_weight = alpha.gather(1, domain_indices.view(-1, 1)).squeeze(1)
        top1_source = torch.argmax(alpha, dim=1)
        top_values, top_indices = torch.topk(alpha, min(self.p_S, self.domain_num), dim=1)
        self._r3_balance_loss = torch.sum(alpha.mean(dim=0) * torch.log((alpha.mean(dim=0) * self.domain_num).clamp_min(1e-9)))
        self._r3_regret_loss = torch.zeros((), device=device)

        regret = None
        source_ce = None
        self_ce = None
        if label is not None:
            label_matrix = label.float().unsqueeze(1).expand_as(candidate_logits)
            source_ce = F.binary_cross_entropy_with_logits(candidate_logits, label_matrix, reduction='none')
            self_ce = source_ce.gather(1, domain_indices.view(-1, 1))
            regret = source_ce - self_ce
            if self._r3_uses_regret():
                non_self = 1.0 - F.one_hot(domain_indices, num_classes=self.domain_num).float()
                regret_for_penalty = regret.detach()
                if self._r3_uses_shuffled_regret() and regret_for_penalty.size(0) > 1:
                    regret_for_penalty = regret_for_penalty[torch.randperm(regret_for_penalty.size(0), device=device)]
                penalty = F.relu(regret_for_penalty + float(self.regret_margin)) * non_self
                self._r3_regret_loss = torch.sum(alpha * penalty, dim=1).mean()

        self._selection_margin_loss = torch.zeros((), device=device)
        self._last_neighbor_diag = {
            'selector_mode': self.selector_mode,
            'reliability_signal': self.reliability_signal,
            'pad_similarity': batch_sims.detach(),
            'base_neighbor_logits': base_logits.detach(),
            'neighbor_logits': router_logits.detach(),
            'selector_scores': router_logits.detach(),
            'selected_neighbor_logits': top_values.detach(),
            'selected_neighbors': top_indices.detach(),
            'deterministic_topk': top_indices.detach(),
            'deterministic_topk_logits': top_values.detach(),
            'r3_alpha': alpha.detach(),
            'r3_router_delta': router_delta.detach(),
            'r3_candidate_logits': candidate_logits.detach(),
            'r3_route_entropy': entropy.detach(),
            'r3_effective_source_num': effective_source_num.detach(),
            'r3_self_route_weight': self_route_weight.detach(),
            'r3_self_route_ratio': (top1_source == domain_indices).float().detach(),
            'r3_top1_source': top1_source.detach(),
            'r3_alpha_mean_per_source': alpha.detach().mean(dim=0),
            'r3_route_balance_loss': self._r3_balance_loss.detach(),
        }
        if reliability_vector is not None:
            self._last_neighbor_diag['r3_reliability_vector'] = reliability_vector.detach()
        if regret is not None:
            self._last_neighbor_diag['r3_regret'] = regret.detach()
            self._last_neighbor_diag['r3_source_ce'] = source_ce.detach()
            self._last_neighbor_diag['r3_self_ce'] = self_ce.detach()
            self._last_neighbor_diag['r3_regret_loss'] = self._r3_regret_loss.detach()

        return fake_news_logits, h_collab

    def forward(self, **kwargs):
        inputs = kwargs['content']
        masks = kwargs['content_masks']
        text_feature = self.bert(inputs, attention_mask=masks)[0]  # ([64, 197, 768])
        image = kwargs['image']
        image_feature = self.image_model.forward_ying(image)  # ([64, 197, 768])
        clip_image = kwargs['clip_image']
        clip_text = kwargs['clip_text']
        domain_indices = kwargs['category'] # Assuming 'category' is the domain index

        # ==================== Existing Feature Extraction (No Changes) ====================
        with torch.no_grad():
            clip_image_feature = self.ClipModel.encode_image(clip_image)
            clip_text_feature = self.ClipModel.encode_text(clip_text)
            clip_image_feature /= clip_image_feature.norm(dim=-1, keepdim=True)
            clip_text_feature /= clip_text_feature.norm(dim=-1, keepdim=True)
        clip_fusion_feature = torch.cat((clip_image_feature, clip_text_feature), dim=-1)
        clip_fusion_feature = self.clip_fusion(clip_fusion_feature.float())

        text_atn_feature = self.text_attention(text_feature, masks)
        image_atn_feature, _ = self.image_attention(image_feature)
        fusion_feature = torch.cat((image_feature, text_feature), dim=-1)
        fusion_atn_feature, _ = self.fusion_attention(fusion_feature)
        fusion_atn_feature = self.MLP_fusion0(fusion_atn_feature)

        text_gate_input, image_gate_input, fusion_gate_input = text_atn_feature, image_atn_feature, fusion_atn_feature

        # Using domain 0 gates as per original logic for expert selection
        text_gate_out = self.text_gate_list[0](text_gate_input)
        image_gate_out = self.image_gate_list[0](image_gate_input)

        text_experts_feature = 0
        text_gate_share_expert_value = 0
        for j in range(self.num_expert):
            text_experts_feature += (self.text_experts[0][j](text_feature) * text_gate_out[:, j].unsqueeze(1))
        for j in range(self.num_expert * 2):
            tmp_expert = self.text_share_expert[0][j](text_feature)
            text_experts_feature += (tmp_expert * text_gate_out[:, (self.num_expert + j)].unsqueeze(1))
            text_gate_share_expert_value += (tmp_expert * text_gate_out[:, (self.num_expert + j)].unsqueeze(1))

        att_text = F.softmax(self.att_mlp_text(text_experts_feature), dim=-1)
        text_gate_expert_value = [att_text[:, 0].view(-1, 1) * text_experts_feature, att_text[:, 1].view(-1, 1) * text_experts_feature]

        image_experts_feature = 0
        image_gate_share_expert_value = 0
        for j in range(self.num_expert):
            image_experts_feature += (self.image_experts[0][j](image_feature) * image_gate_out[:, j].unsqueeze(1))
        for j in range(self.num_expert * 2):
            tmp_expert = self.image_share_expert[0][j](image_feature)
            image_experts_feature += (tmp_expert * image_gate_out[:, (self.num_expert + j)].unsqueeze(1))
            image_gate_share_expert_value += (tmp_expert * image_gate_out[:, (self.num_expert + j)].unsqueeze(1))

        att_img = F.softmax(self.att_mlp_img(image_experts_feature), dim=-1)
        image_gate_expert_value = [att_img[:, 0].view(-1, 1) * image_experts_feature, att_img[:, 1].view(-1, 1) * image_experts_feature]

        fusion_share_feature = self.MLP_fusion(torch.cat((clip_fusion_feature, text_gate_share_expert_value, image_gate_share_expert_value), dim=-1))
        fusion_gate_out0 = self.fusion_gate_list0[0](self.domain_fusion(fusion_share_feature))

        fusion_experts_feature = 0
        for n in range(self.num_expert):
            fusion_experts_feature += (self.fusion_experts[0][n](fusion_share_feature) * fusion_gate_out0[:, n].unsqueeze(1))
        for n in range(self.num_expert * 2):
            fusion_experts_feature += (self.fusion_share_expert[0][n](fusion_share_feature) * fusion_gate_out0[:, (self.num_expert + n)].unsqueeze(1))

        att_mm = F.softmax(self.att_mlp_mm(fusion_experts_feature), dim=-1)
        fusion_gate_expert_value0 = [att_mm[:, 0].view(-1, 1) * fusion_experts_feature, att_mm[:, 1].view(-1, 1) * fusion_experts_feature]

        text_features = text_gate_expert_value[0]
        image_features = image_gate_expert_value[0]
        fusion_features = fusion_gate_expert_value0[0]

        aux_text_features = text_features.detach() if self.training and self.aux_detach_features else text_features
        aux_image_features = image_features.detach() if self.training and self.aux_detach_features else image_features
        aux_fusion_features = fusion_features.detach() if self.training and self.aux_detach_features else fusion_features
        text_fake_news_logits = self.text_classifier(aux_text_features).squeeze(1)
        image_fake_news_logits = self.image_classifier(aux_image_features).squeeze(1)
        fusion_fake_news_logits = self.fusion_classifier(aux_fusion_features).squeeze(1)
        text_fake_news = torch.sigmoid(text_fake_news_logits)
        image_fake_news = torch.sigmoid(image_fake_news_logits)
        fusion_fake_news = torch.sigmoid(fusion_fake_news_logits)
        reliability_score = None
        reliability_vector = self._reliability_vector(
            text_fake_news,
            image_fake_news,
            fusion_fake_news,
            clip_image_feature=clip_image_feature,
            clip_text_feature=clip_text_feature)
        if self.selector_mode == 'reliability':
            reliability_score = self._reliability_score(
                text_fake_news,
                image_fake_news,
                fusion_fake_news,
                clip_image_feature=clip_image_feature,
                clip_text_feature=clip_text_feature)
            self._update_reliability_domain_stats(domain_indices, reliability_score)

        # This is h_{d_i}
        h_di = text_features + image_features + fusion_features



        # 2.3.1 Prototype Learning and Reconstruction Loss Calculation
        encoded_h = self.proto_encoder(h_di)
        # For each sample, find the closest prototype within its own domain
        protos_for_batch = self.domain_prototypes[domain_indices] # (Batch, M, Dim)
        dist_to_protos = torch.cdist(encoded_h.unsqueeze(1), protos_for_batch) # (Batch, 1, M)
        _, closest_proto_indices = torch.min(dist_to_protos, dim=2) # (Batch, 1)

        # Gather the quantized vectors
        quantized_h = protos_for_batch.gather(1, closest_proto_indices.unsqueeze(2).expand(-1, -1, h_di.shape[1])).squeeze(1)

        reconstructed_h = self.proto_decoder(quantized_h)
        loss_rec = F.mse_loss(reconstructed_h, h_di)

        # 2.3.2 Calculate Prototype-based Asymmetric Distance (PAD)
        dist_matrix = self._calculate_pad() # (D_s, D_t)

        sim_matrix = 1.0 / (dist_matrix + 1e-6)
        target_prompts = self.domain_modal_prompts[domain_indices] # (Batch, 3*Lp, Dp)
        batch_size = h_di.size(0)

        if self._is_r3_mode():
            label = kwargs.get('label', None)
            fake_news_logits, h_collab = self._run_r3_regret_soft_router(
                h_di, target_prompts, sim_matrix, domain_indices, reliability_vector, label=label)
        else:
            # 2.4.1 Gumbel-based Neighbor Selector (GNS)
            self._r3_regret_loss = None
            self._r3_balance_loss = None
            self._current_reliability_score = reliability_score
            neighbor_indices = self._gumbel_neighbor_selector(sim_matrix, domain_indices) # (Batch, S)
            self._current_reliability_score = None

            # 2.4.2 Domain-Collaborative Attention (DCA)
            neighbor_prompts = self.domain_modal_prompts[neighbor_indices.view(-1)].view(batch_size, self.p_S, 3 * self.p_Lp, self.p_Dp)
            neighbor_prompts_flat = neighbor_prompts.view(batch_size, -1, self.p_Dp)
            key_padding_mask = torch.ones(batch_size, self.p_S * 3 * self.p_Lp, device=h_di.device)
            collaborated_prompts = self.dca_module(target_prompts, neighbor_prompts_flat, neighbor_prompts_flat, key_padding_mask)
            h_collab = torch.mean(collaborated_prompts, dim=1) # (Batch, Dp)
            h_final = torch.cat([h_di, h_collab], dim=1)
            fake_news_logits = self.final_classifier_panda(h_final).squeeze(1)
        fake_news_sigmoid = torch.sigmoid(fake_news_logits)


        return fake_news_sigmoid, text_fake_news, image_fake_news, fusion_fake_news, loss_rec





class Trainer():
    def __init__(self,
                 emb_dim,
                 mlp_dims,
                 bert,
                 use_cuda,
                 lr,
                 dropout,
                 train_loader,
                 val_loader,
                 test_loader,
                 category_dict,
                 weight_decay,
                 save_param_dir,
                 loss_weight=[1, 0.006, 0.009, 5e-5],
                 lambda_rec=0.1, # Hyperparameter for reconstruction loss
                 domain_num=9, # Number of domains
                 early_stop=5,
                 epoches=100,
                 dataset_type=None,
                 skip_final_test=False,
                 selector_mode='panda_gumbel',
                 reliability_signal='branch_fusion',
                 reliability_lambda=0.05,
                 reliability_gating='distance',
                 reliability_stats_mode='online',
                 reliability_ema_momentum=0.9,
                 selection_margin_lambda=0.0,
                 selection_margin=0.1,
                 aux_loss_weight=1.0,
                 aux_text_weight=None,
                 aux_image_weight=None,
                 aux_fusion_weight=None,
                 aux_schedule='constant',
                 aux_schedule_start=1.0,
                 aux_schedule_end=1.0,
                 aux_label_mode='true',
                 aux_label_seed=None,
                 aux_random_label_seed=None,
                 aux_shuffle_seed=None,
                 aux_detach_features=False,
                 r5a_grad_mode='none',
                 r5a_log_dir=None,
                 r5a_log_interval=1,
                 uea_aux_mode='none',
                 uea_utility_csv=None,
                 uea_alpha_max=0.5,
                 uea_weight_floor=1e-8,
                 uea_seed=None,
                 uea_boundary_low_margin_quantile=0.25,
                 uea_boundary_risk_quantile=0.75,
                 regret_lambda=0.0,
                 route_balance_lambda=0.0,
                 regret_margin=0.0,
                 router_tau_start=2.0,
                 router_tau_end=1.0,
                 adapter_dim=64,
                 router_hidden=128
                 ):
        self.lr = lr
        self.weight_decay = weight_decay
        self.train_loader = train_loader
        self.test_loader = test_loader
        self.val_loader = val_loader
        self.early_stop = early_stop
        self.epoches = epoches
        self.category_dict = category_dict
        self.loss_weight = loss_weight
        self.use_cuda = use_cuda
        self.lambda_rec = lambda_rec
        self.domain_num = domain_num
        self.dataset_type = dataset_type
        self.skip_final_test = skip_final_test
        self.selector_mode = 'panda_gumbel' if selector_mode == 'gumbel' else selector_mode
        self.reliability_signal = reliability_signal
        self.reliability_lambda = reliability_lambda
        self.reliability_gating = reliability_gating
        self.reliability_stats_mode = reliability_stats_mode
        self.reliability_ema_momentum = reliability_ema_momentum
        self.selection_margin_lambda = selection_margin_lambda
        self.selection_margin = selection_margin
        self.aux_loss_weight = aux_loss_weight
        self.aux_text_weight = aux_loss_weight if aux_text_weight is None else aux_text_weight
        self.aux_image_weight = aux_loss_weight if aux_image_weight is None else aux_image_weight
        self.aux_fusion_weight = aux_loss_weight if aux_fusion_weight is None else aux_fusion_weight
        self.aux_schedule = aux_schedule
        self.aux_schedule_start = aux_schedule_start
        self.aux_schedule_end = aux_schedule_end
        self.aux_label_mode = aux_label_mode
        self.aux_label_seed = aux_label_seed
        self.aux_random_label_seed = aux_random_label_seed
        self.aux_shuffle_seed = aux_shuffle_seed
        self._aux_label_generator = None
        self._aux_label_generator_device = None
        self._aux_label_generator_seed = None
        self.aux_detach_features = aux_detach_features
        self.r5a_grad_mode = r5a_grad_mode
        self.r5a_log_dir = r5a_log_dir
        self.r5a_log_interval = max(int(r5a_log_interval), 1)
        self._dwa_prev_task_losses = None
        self.uea_aux_mode = uea_aux_mode
        self.uea_utility_csv = uea_utility_csv
        self.uea_alpha_max = float(uea_alpha_max)
        self.uea_weight_floor = float(uea_weight_floor)
        self.uea_seed = uea_seed
        self.uea_boundary_low_margin_quantile = float(uea_boundary_low_margin_quantile)
        self.uea_boundary_risk_quantile = float(uea_boundary_risk_quantile)
        self._uea_unit_weights_cpu = None
        self._uea_unit_weights_device = None
        self._uea_unit_weights_device_key = None
        self._uea_alpha_cpu = None
        self._uea_meta = None
        self.regret_lambda = regret_lambda
        self.route_balance_lambda = route_balance_lambda
        self.regret_margin = regret_margin
        self.router_tau_start = router_tau_start
        self.router_tau_end = router_tau_end
        self.adapter_dim = adapter_dim
        self.router_hidden = router_hidden

        self.emb_dim = emb_dim
        self.mlp_dims = mlp_dims
        self.bert = bert
        self.dropout = dropout
        os.makedirs(save_param_dir, exist_ok=True)
        self.save_param_dir = save_param_dir

        if self.uea_aux_mode != 'none':
            if self.r5a_grad_mode != 'none':
                raise ValueError('Round11 UEA aux allocation is only supported with r5a_grad_mode=none.')
            self._load_uea_branch_weights()

    @staticmethod
    def _uea_normalize_rows(values):
        arr = np.clip(np.asarray(values, dtype=np.float64), 0.0, None)
        denom = arr.sum(axis=1, keepdims=True)
        out = arr / np.clip(denom, 1e-12, None)
        zero = denom.reshape(-1) < 1e-12
        if np.any(zero):
            out[zero] = 1.0 / arr.shape[1]
        return out

    @staticmethod
    def _uea_entropy(q):
        arr = np.clip(np.asarray(q, dtype=np.float64), 1e-12, 1.0)
        return -np.sum(arr * np.log(arr), axis=1) / math.log(arr.shape[1])

    @staticmethod
    def _uea_minmax(values):
        arr = np.asarray(values, dtype=np.float64)
        return float(np.nanmin(arr)), float(np.nanmax(arr))

    @staticmethod
    def _uea_minmax_apply(values, lo, hi):
        arr = np.asarray(values, dtype=np.float64)
        return np.clip((arr - lo) / max(float(hi) - float(lo), 1e-12), 0.0, 1.0)

    def _load_uea_branch_weights(self):
        if not self.uea_utility_csv:
            raise ValueError('uea_utility_csv is required when uea_aux_mode is enabled.')
        rows = []
        with open(self.uea_utility_csv, newline='', encoding='utf-8') as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                if row.get('split') != 'train':
                    raise ValueError(f"UEA only accepts train utility rows, got split={row.get('split')}")
                rows.append(row)
        if not rows:
            raise ValueError(f'No rows found in UEA utility CSV: {self.uea_utility_csv}')

        sample_ids = np.asarray([int(row['sample_id']) for row in rows], dtype=np.int64)
        if len(np.unique(sample_ids)) != len(sample_ids):
            raise ValueError('UEA utility CSV has duplicate sample_id values.')
        order = np.argsort(sample_ids, kind='mergesort')
        sample_ids = sample_ids[order]
        expected = np.arange(int(sample_ids.max()) + 1, dtype=np.int64)
        if len(sample_ids) != len(expected) or not np.array_equal(sample_ids, expected):
            raise ValueError('UEA utility CSV sample_id values must be contiguous from 0.')
        rows = [rows[int(i)] for i in order]

        q_target = np.asarray(
            [[float(row[f'q_target_{branch}']) for branch in ('text', 'image', 'fusion')] for row in rows],
            dtype=np.float64)
        utility = np.asarray(
            [[float(row[f'u_{branch}']) for branch in ('text', 'image', 'fusion')] for row in rows],
            dtype=np.float64)
        prob = np.asarray(
            [[float(row[f'p_{branch}']) for branch in ('text', 'image', 'fusion')] for row in rows],
            dtype=np.float64)

        mode = self.uea_aux_mode
        rng_seed = int(self.uea_seed if self.uea_seed is not None else 0)
        if mode in ['utility_only', 'entropy', 'boundary_entropy']:
            q = self._uea_normalize_rows(q_target + self.uea_weight_floor)
        elif mode == 'shuffled_utility':
            rng = np.random.default_rng(rng_seed)
            q = self._uea_normalize_rows(q_target[rng.permutation(len(q_target))] + self.uea_weight_floor)
        elif mode == 'random_utility':
            rng = np.random.default_rng(rng_seed)
            q = rng.dirichlet(np.ones(3), size=len(rows))
        elif mode == 'reverse_utility':
            q = self._uea_normalize_rows(np.maximum(-utility, 0.0) + self.uea_weight_floor)
        elif mode == 'confidence':
            q = self._uea_normalize_rows(np.abs(2.0 * prob - 1.0) + self.uea_weight_floor)
        else:
            raise ValueError(f'Unknown uea_aux_mode: {mode}')

        if mode == 'utility_only':
            alpha = np.full(len(rows), self.uea_alpha_max, dtype=np.float64)
            boundary_rate = None
        else:
            utility_confidence = 1.0 - self._uea_entropy(q)
            alpha = self.uea_alpha_max * utility_confidence
            boundary_rate = None
            if mode == 'boundary_entropy':
                margin = np.asarray([float(row['final_margin_abs']) for row in rows], dtype=np.float64)
                risk = self._uea_minmax_apply(-margin, *self._uea_minmax(-margin))
                for name in ('confidence_uncertainty', 'branch_disagreement', 'fusion_uncertainty'):
                    values = np.asarray([float(row[name]) for row in rows], dtype=np.float64)
                    risk += self._uea_minmax_apply(values, *self._uea_minmax(values))
                risk = risk / 4.0
                low_margin_thr = float(np.quantile(margin, self.uea_boundary_low_margin_quantile))
                risk_thr = float(np.quantile(risk, self.uea_boundary_risk_quantile))
                boundary = (margin <= low_margin_thr) | (risk >= risk_thr)
                alpha = alpha * boundary.astype(np.float64)
                boundary_rate = float(np.mean(boundary))
        alpha = np.clip(alpha, 0.0, self.uea_alpha_max)
        unit_weights = (1.0 - alpha[:, None]) / 3.0 + alpha[:, None] * q
        unit_weights = unit_weights / np.clip(unit_weights.sum(axis=1, keepdims=True), 1e-12, None)

        self._uea_unit_weights_cpu = torch.tensor(unit_weights, dtype=torch.float32)
        self._uea_alpha_cpu = torch.tensor(alpha, dtype=torch.float32)
        self._uea_meta = {
            'mode': mode,
            'rows': int(len(rows)),
            'alpha_max': float(self.uea_alpha_max),
            'alpha_mean': float(np.mean(alpha)),
            'alpha_active_rate': float(np.mean(alpha > 1e-12)),
            'q_entropy_mean': float(np.mean(self._uea_entropy(q))),
            'w_text_mean': float(np.mean(unit_weights[:, 0])),
            'w_image_mean': float(np.mean(unit_weights[:, 1])),
            'w_fusion_mean': float(np.mean(unit_weights[:, 2])),
            'top_weight_text_rate': float(np.mean(np.argmax(unit_weights, axis=1) == 0)),
            'top_weight_image_rate': float(np.mean(np.argmax(unit_weights, axis=1) == 1)),
            'top_weight_fusion_rate': float(np.mean(np.argmax(unit_weights, axis=1) == 2)),
            'boundary_rate': boundary_rate,
            'utility_csv': self.uea_utility_csv,
        }

    def _uea_weights_for_batch(self, sample_id, device):
        if self._uea_unit_weights_cpu is None:
            return None
        if sample_id is None:
            raise ValueError('UEA aux allocation requires sample_id in the training batch.')
        device_key = str(device)
        if self._uea_unit_weights_device is None or self._uea_unit_weights_device_key != device_key:
            self._uea_unit_weights_device = self._uea_unit_weights_cpu.to(device)
            self._uea_unit_weights_device_key = device_key
        return self._uea_unit_weights_device.index_select(0, sample_id.long())

    def _uea_weighted_aux_loss(self, aux_per_sample_losses, aux_weights, sample_id, device):
        unit_weights = self._uea_weights_for_batch(sample_id, device)
        branch_losses = torch.stack([
            aux_per_sample_losses['text_branch'].view(-1),
            aux_per_sample_losses['image_branch'].view(-1),
            aux_per_sample_losses['fusion_branch'].view(-1),
        ], dim=1)
        base_budget = (
            float(aux_weights['text_branch'])
            + float(aux_weights['image_branch'])
            + float(aux_weights['fusion_branch'])
        ) / 3.0
        return (branch_losses * unit_weights * base_budget).sum(dim=1).mean()

    def _r5a_param_groups(self):
        return {
            'text_branch': self._unique_trainable_params([
                self.model.text_experts,
                self.model.text_share_expert,
                self.model.att_mlp_text,
            ]),
            'image_branch': self._unique_trainable_params([
                self.model.image_experts,
                self.model.image_share_expert,
                self.model.att_mlp_img,
            ]),
            'fusion_branch': self._unique_trainable_params([
                self.model.fusion_experts,
                self.model.fusion_share_expert,
                self.model.fusion_gate_list0,
                self.model.domain_fusion,
                self.model.MLP_fusion,
                self.model.att_mlp_mm,
            ]),
            'all_trainable': self._unique_trainable_params([self.model]),
        }

    @staticmethod
    def _unique_trainable_params(modules):
        seen = set()
        params = []
        for module in modules:
            for param in module.parameters():
                if param.requires_grad and id(param) not in seen:
                    seen.add(id(param))
                    params.append(param)
        return params

    @staticmethod
    def _flatten_grads(grads):
        pieces = []
        for grad in grads:
            if grad is not None:
                pieces.append(grad.detach().reshape(-1).float())
        if not pieces:
            return None
        return torch.cat(pieces)

    @staticmethod
    def _r5a_grad_stats(final_grads, aux_grads):
        gf = Trainer._flatten_grads(final_grads)
        ga = Trainer._flatten_grads(aux_grads)
        if gf is None or ga is None:
            return {
                'cosine': None,
                'final_norm': 0.0,
                'aux_norm': 0.0,
                'norm_ratio_aux_over_final': None,
            }
        final_norm = torch.norm(gf)
        aux_norm = torch.norm(ga)
        denom = torch.clamp(final_norm * aux_norm, min=1e-12)
        cosine = torch.dot(gf, ga) / denom
        return {
            'cosine': float(cosine.detach().cpu()),
            'final_norm': float(final_norm.detach().cpu()),
            'aux_norm': float(aux_norm.detach().cpu()),
            'norm_ratio_aux_over_final': float((aux_norm / torch.clamp(final_norm, min=1e-12)).detach().cpu()),
        }

    @staticmethod
    def _set_grads(params, grads):
        for param, grad in zip(params, grads):
            if grad is None:
                param.grad = None
            else:
                param.grad = grad.detach().clone()

    @staticmethod
    def _combine_grads(base_grads, aux_grads):
        combined = []
        for base, aux in zip(base_grads, aux_grads):
            if base is None and aux is None:
                combined.append(None)
            elif base is None:
                combined.append(aux)
            elif aux is None:
                combined.append(base)
            else:
                combined.append(base + aux)
        return combined

    @staticmethod
    def _project_conflicting_grads(base_grads, aux_grads, random_sign=False):
        projected = []
        for base, aux in zip(base_grads, aux_grads):
            if aux is None:
                projected.append(None)
                continue
            if base is None:
                projected.append(aux)
                continue
            dot = torch.sum(base * aux)
            denom = torch.sum(base * base).clamp_min(1e-12)
            if dot < 0:
                direction = -1.0 if random_sign and bool(torch.randint(0, 2, (), device=aux.device).item()) else 1.0
                projected.append(aux - direction * dot / denom * base)
            else:
                projected.append(aux)
        return projected

    @staticmethod
    def _cagrad_aux_grads(final_grads, aux_grads):
        projected = []
        for final, aux in zip(final_grads, aux_grads):
            if aux is None:
                projected.append(None)
                continue
            if final is None:
                projected.append(aux)
                continue
            dot = torch.sum(final * aux)
            final_norm_sq = torch.sum(final * final).clamp_min(1e-12)
            alpha = torch.clamp(-dot / final_norm_sq, min=0.0, max=1.0)
            projected.append(aux + alpha * final)
        return projected

    def _r5a_prepare_logger(self):
        if not self.r5a_log_dir:
            return None, None
        os.makedirs(self.r5a_log_dir, exist_ok=True)
        path = os.path.join(self.r5a_log_dir, 'r5a_train_gradient_telemetry.csv')
        fieldnames = [
            'epoch',
            'step',
            'mode',
            'branch',
            'cosine',
            'final_norm',
            'aux_norm',
            'norm_ratio_aux_over_final',
            'conflict_cos_lt_0',
            'strong_conflict_cos_lt_neg0p1',
            'loss_final',
            'loss_text',
            'loss_image',
            'loss_fusion',
            'loss_rec',
            'loss_total',
            'aux_loss_weight',
            'aux_text_weight_effective',
            'aux_image_weight_effective',
            'aux_fusion_weight_effective',
            'aux_effective_loss',
            'aux_schedule',
            'aux_label_mode',
            'aux_label_seed',
            'aux_random_label_seed',
            'aux_shuffle_seed',
            'aux_detach_features',
        ]
        handle = open(path, 'w', newline='', encoding='utf-8')
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        return handle, writer

    def _r5a_log_stats(self, writer, epoch, step, mode, branch, stats, losses):
        if writer is None or (step % self.r5a_log_interval) != 0:
            return
        cosine = stats.get('cosine')
        writer.writerow({
            'epoch': int(epoch + 1),
            'step': int(step),
            'mode': mode,
            'branch': branch,
            'cosine': '' if cosine is None else cosine,
            'final_norm': stats.get('final_norm'),
            'aux_norm': stats.get('aux_norm'),
            'norm_ratio_aux_over_final': '' if stats.get('norm_ratio_aux_over_final') is None else stats.get('norm_ratio_aux_over_final'),
            'conflict_cos_lt_0': bool(cosine is not None and cosine < 0.0),
            'strong_conflict_cos_lt_neg0p1': bool(cosine is not None and cosine < -0.1),
            'loss_final': losses['final'],
            'loss_text': losses['text'],
            'loss_image': losses['image'],
            'loss_fusion': losses['fusion'],
            'loss_rec': losses['rec'],
            'loss_total': losses['total'],
            'aux_loss_weight': self.aux_loss_weight,
            'aux_text_weight_effective': losses['aux_text_weight_effective'],
            'aux_image_weight_effective': losses['aux_image_weight_effective'],
            'aux_fusion_weight_effective': losses['aux_fusion_weight_effective'],
            'aux_effective_loss': losses['aux_effective'],
            'aux_schedule': self.aux_schedule,
            'aux_label_mode': self.aux_label_mode,
            'aux_label_seed': '' if self.aux_label_seed is None else self.aux_label_seed,
            'aux_random_label_seed': '' if self.aux_random_label_seed is None else self.aux_random_label_seed,
            'aux_shuffle_seed': '' if self.aux_shuffle_seed is None else self.aux_shuffle_seed,
            'aux_detach_features': self.aux_detach_features,
        })

    def _aux_schedule_multiplier(self, epoch, step, steps_per_epoch):
        total_steps = max(int(self.epoches) * max(int(steps_per_epoch), 1) - 1, 1)
        global_step = int(epoch) * max(int(steps_per_epoch), 1) + int(step)
        progress = min(max(float(global_step) / float(total_steps), 0.0), 1.0)
        if self.aux_schedule == 'constant':
            shaped_progress = 1.0
        elif self.aux_schedule == 'linear_ramp_up':
            shaped_progress = progress
        elif self.aux_schedule == 'linear_ramp_down':
            shaped_progress = 1.0 - progress
        elif self.aux_schedule == 'cosine_ramp_up':
            shaped_progress = 0.5 - 0.5 * math.cos(math.pi * progress)
        elif self.aux_schedule == 'cosine_ramp_down':
            shaped_progress = 0.5 + 0.5 * math.cos(math.pi * progress)
        else:
            raise ValueError(f'Unknown aux_schedule: {self.aux_schedule}')
        if self.aux_schedule == 'constant':
            return 1.0
        return float(self.aux_schedule_start) + (float(self.aux_schedule_end) - float(self.aux_schedule_start)) * shaped_progress

    def _current_aux_weights(self, epoch, step, steps_per_epoch):
        multiplier = self._aux_schedule_multiplier(epoch, step, steps_per_epoch)
        return {
            'text_branch': float(self.aux_text_weight) * multiplier,
            'image_branch': float(self.aux_image_weight) * multiplier,
            'fusion_branch': float(self.aux_fusion_weight) * multiplier,
        }

    def _aux_label_target(self, label):
        if self.aux_label_mode == 'true':
            return label.float()
        generator = None
        label_seed = self.aux_label_seed
        if self.aux_label_mode == 'random' and self.aux_random_label_seed is not None:
            label_seed = self.aux_random_label_seed
        if self.aux_label_mode == 'shuffled' and self.aux_shuffle_seed is not None:
            label_seed = self.aux_shuffle_seed
        if label_seed is not None:
            label_device = str(label.device)
            if (
                self._aux_label_generator is None
                or self._aux_label_generator_device != label_device
                or self._aux_label_generator_seed != int(label_seed)
            ):
                self._aux_label_generator = torch.Generator(device=label.device)
                self._aux_label_generator.manual_seed(int(label_seed))
                self._aux_label_generator_device = label_device
                self._aux_label_generator_seed = int(label_seed)
            generator = self._aux_label_generator
        if self.aux_label_mode == 'random':
            return torch.randint(0, 2, label.shape, device=label.device, generator=generator).float()
        if self.aux_label_mode == 'shuffled':
            if label.numel() <= 1:
                return 1.0 - label.float()
            return label[torch.randperm(label.size(0), device=label.device, generator=generator)].float()
        raise ValueError(f'Unknown aux_label_mode: {self.aux_label_mode}')

    @staticmethod
    def _weighted_aux_loss(aux_losses, aux_weights):
        return (
            aux_weights['text_branch'] * aux_losses['text_branch']
            + aux_weights['image_branch'] * aux_losses['image_branch']
            + aux_weights['fusion_branch'] * aux_losses['fusion_branch']
        ) / 3.0

    def _generic_gradnorm_loss(self, final_loss, aux_losses):
        task_losses = [
            final_loss,
            aux_losses['text_branch'],
            aux_losses['image_branch'],
            aux_losses['fusion_branch'],
        ]
        detached = [loss.detach() for loss in task_losses]
        mean_loss = torch.stack(detached).mean().clamp_min(1e-12)
        weights = [float((mean_loss / loss.clamp_min(1e-12)).detach().cpu()) for loss in detached]
        return sum(weight * loss for weight, loss in zip(weights, task_losses)) / len(task_losses)

    def _generic_dwa_loss(self, final_loss, aux_losses):
        task_losses = [
            final_loss,
            aux_losses['text_branch'],
            aux_losses['image_branch'],
            aux_losses['fusion_branch'],
        ]
        current = torch.stack([loss.detach() for loss in task_losses])
        if self._dwa_prev_task_losses is None:
            weights = torch.ones_like(current)
        else:
            ratio = current / self._dwa_prev_task_losses.clamp_min(1e-12)
            weights = torch.softmax(ratio / 2.0, dim=0) * len(task_losses)
        self._dwa_prev_task_losses = current.detach()
        return sum(float(weight.detach().cpu()) * loss for weight, loss in zip(weights, task_losses)) / len(task_losses)

    def _r5a_backward(self, loss, final_loss, aux_losses, aux_weights, optimizer, groups, epoch, step, writer):
        mode = self.r5a_grad_mode
        if mode in ['none', 'same_budget_noop']:
            optimizer.zero_grad()
            if writer is not None or mode == 'same_budget_noop':
                losses = self._r5a_loss_values(loss, final_loss, aux_losses, aux_weights)
                for branch, params in groups.items():
                    if branch == 'all_trainable':
                        continue
                    final_grads = torch.autograd.grad(final_loss, params, retain_graph=True, allow_unused=True)
                    aux_grads = torch.autograd.grad(aux_losses[branch], params, retain_graph=True, allow_unused=True)
                    stats = self._r5a_grad_stats(final_grads, aux_grads)
                    self._r5a_log_stats(writer, epoch, step, mode, branch, stats, losses)
            loss.backward()
            return

        all_params = groups['all_trainable']
        optimizer.zero_grad()
        losses = self._r5a_loss_values(loss, final_loss, aux_losses, aux_weights)
        for branch, params in groups.items():
            if branch == 'all_trainable':
                continue
            final_grads = torch.autograd.grad(final_loss, params, retain_graph=True, allow_unused=True)
            aux_grads = torch.autograd.grad(aux_losses[branch], params, retain_graph=True, allow_unused=True)
            stats = self._r5a_grad_stats(final_grads, aux_grads)
            self._r5a_log_stats(writer, epoch, step, mode, branch, stats, losses)
        if mode == 'generic_pcgrad':
            final_with_rec = final_loss + self.lambda_rec * self._r5a_current_rec_loss
            final_grads_all = torch.autograd.grad(final_with_rec, all_params, retain_graph=True, allow_unused=True)
            aux_total = self._weighted_aux_loss(aux_losses, aux_weights)
            aux_grads_all = torch.autograd.grad(aux_total, all_params, retain_graph=True, allow_unused=True)
            aux_grads_all = self._project_conflicting_grads(final_grads_all, aux_grads_all)
            self._set_grads(all_params, self._combine_grads(final_grads_all, aux_grads_all))
        elif mode == 'generic_cagrad':
            final_with_rec = final_loss + self.lambda_rec * self._r5a_current_rec_loss
            final_grads_all = torch.autograd.grad(final_with_rec, all_params, retain_graph=True, allow_unused=True)
            aux_total = self._weighted_aux_loss(aux_losses, aux_weights)
            aux_grads_all = torch.autograd.grad(aux_total, all_params, retain_graph=True, allow_unused=True)
            aux_grads_all = self._cagrad_aux_grads(final_grads_all, aux_grads_all)
            self._set_grads(all_params, self._combine_grads(final_grads_all, aux_grads_all))
        elif mode == 'generic_gradnorm':
            balanced_loss = self._generic_gradnorm_loss(final_loss, aux_losses) + self.lambda_rec * self._r5a_current_rec_loss
            balanced_loss.backward()
        elif mode == 'generic_dwa':
            balanced_loss = self._generic_dwa_loss(final_loss, aux_losses) + self.lambda_rec * self._r5a_current_rec_loss
            balanced_loss.backward()
        elif mode in ['dgl_branch_pcgrad', 'dgl_branch_conflict_drop']:
            final_with_rec = final_loss + self.lambda_rec * self._r5a_current_rec_loss
            final_grads_all = torch.autograd.grad(final_with_rec, all_params, retain_graph=True, allow_unused=True)
            grad_by_param = {}
            for param, grad in zip(all_params, final_grads_all):
                if grad is not None:
                    grad_by_param[id(param)] = grad.detach().clone()

            aux_head_groups = {
                'text_branch': self._unique_trainable_params([self.model.text_classifier]),
                'image_branch': self._unique_trainable_params([self.model.image_classifier]),
                'fusion_branch': self._unique_trainable_params([self.model.fusion_classifier]),
            }
            for branch in ['text_branch', 'image_branch', 'fusion_branch']:
                branch_shared_params = list(groups[branch])
                branch_params = []
                seen = set()
                for param in branch_shared_params + list(aux_head_groups[branch]):
                    if param.requires_grad and id(param) not in seen:
                        seen.add(id(param))
                        branch_params.append(param)
                if not branch_params:
                    continue
                branch_final_grads = torch.autograd.grad(final_with_rec, branch_params, retain_graph=True, allow_unused=True)
                branch_aux_loss = aux_weights[branch] * aux_losses[branch] / 3.0
                branch_aux_grads = torch.autograd.grad(branch_aux_loss, branch_params, retain_graph=True, allow_unused=True)
                if mode == 'dgl_branch_pcgrad':
                    branch_aux_grads = self._project_conflicting_grads(branch_final_grads, branch_aux_grads)
                else:
                    shared_final_grads = torch.autograd.grad(final_with_rec, branch_shared_params, retain_graph=True, allow_unused=True)
                    shared_aux_grads = torch.autograd.grad(branch_aux_loss, branch_shared_params, retain_graph=True, allow_unused=True)
                    stats = self._r5a_grad_stats(shared_final_grads, shared_aux_grads)
                    if stats.get('cosine') is not None and stats['cosine'] < 0.0:
                        branch_aux_grads = [None for _ in branch_aux_grads]
                for param, aux_grad in zip(branch_params, branch_aux_grads):
                    if aux_grad is None:
                        continue
                    key = id(param)
                    if key in grad_by_param:
                        grad_by_param[key] = grad_by_param[key] + aux_grad.detach()
                    else:
                        grad_by_param[key] = aux_grad.detach().clone()

            for param in all_params:
                grad = grad_by_param.get(id(param))
                param.grad = None if grad is None else grad.clone()
        elif mode == 'random_sign':
            final_with_rec = final_loss + self.lambda_rec * self._r5a_current_rec_loss
            final_grads_all = torch.autograd.grad(final_with_rec, all_params, retain_graph=True, allow_unused=True)
            aux_total = self._weighted_aux_loss(aux_losses, aux_weights)
            aux_grads_all = torch.autograd.grad(aux_total, all_params, retain_graph=True, allow_unused=True)
            aux_grads_all = self._project_conflicting_grads(final_grads_all, aux_grads_all, random_sign=True)
            self._set_grads(all_params, self._combine_grads(final_grads_all, aux_grads_all))
        elif mode == 'image_project':
            image_params = groups['image_branch']
            base_loss = final_loss + self.lambda_rec * self._r5a_current_rec_loss
            base_loss = base_loss + (
                aux_weights['text_branch'] * aux_losses['text_branch']
                + aux_weights['fusion_branch'] * aux_losses['fusion_branch']
            ) / 3.0
            base_grads_img = torch.autograd.grad(base_loss, image_params, retain_graph=True, allow_unused=True)
            final_grads_img = torch.autograd.grad(final_loss, image_params, retain_graph=True, allow_unused=True)
            image_aux = aux_weights['image_branch'] * aux_losses['image_branch'] / 3.0
            aux_grads_img = torch.autograd.grad(image_aux, image_params, retain_graph=True, allow_unused=True)
            projected = self._project_conflicting_grads(final_grads_img, aux_grads_img)
            loss.backward()
            for param, base_grad, aux_grad in zip(image_params, base_grads_img, projected):
                if base_grad is None and aux_grad is None:
                    param.grad = None
                elif base_grad is None:
                    param.grad = aux_grad.detach().clone()
                elif aux_grad is None:
                    param.grad = base_grad.detach().clone()
                else:
                    param.grad = (base_grad + aux_grad).detach().clone()
        else:
            raise ValueError(f'Unknown r5a_grad_mode: {mode}')

    def _r5a_loss_values(self, loss, final_loss, aux_losses, aux_weights):
        return {
            'final': float(final_loss.detach().cpu()),
            'text': float(aux_losses['text_branch'].detach().cpu()),
            'image': float(aux_losses['image_branch'].detach().cpu()),
            'fusion': float(aux_losses['fusion_branch'].detach().cpu()),
            'rec': float(self._r5a_current_rec_loss.detach().cpu()),
            'total': float(loss.detach().cpu()),
            'aux_effective': float(self._weighted_aux_loss(aux_losses, aux_weights).detach().cpu()),
            'aux_text_weight_effective': float(aux_weights['text_branch']),
            'aux_image_weight_effective': float(aux_weights['image_branch']),
            'aux_fusion_weight_effective': float(aux_weights['fusion_branch']),
        }

    def train(self):
        # Pass domain_num to the model
        self.model = MultiDomainPLEFENDModel(
            self.emb_dim,
            self.mlp_dims,
            self.bert,
            320,
            self.dropout,
            self.domain_num,
            selector_mode=self.selector_mode,
            reliability_signal=self.reliability_signal,
            reliability_lambda=self.reliability_lambda,
            reliability_gating=self.reliability_gating,
            reliability_stats_mode=self.reliability_stats_mode,
            reliability_ema_momentum=self.reliability_ema_momentum,
            selection_margin_lambda=self.selection_margin_lambda,
            selection_margin=self.selection_margin,
            regret_lambda=self.regret_lambda,
            route_balance_lambda=self.route_balance_lambda,
            regret_margin=self.regret_margin,
            router_tau_start=self.router_tau_start,
            router_tau_end=self.router_tau_end,
            adapter_dim=self.adapter_dim,
            router_hidden=self.router_hidden,
            aux_detach_features=self.aux_detach_features)
        if self.use_cuda:
            self.model = self.model.cuda()
        print('selector_mode: {}; reliability_signal: {}; reliability_lambda: {}; reliability_gating: {}; reliability_stats_mode: {}; selection_margin_lambda: {}; selection_margin: {}; aux_loss_weight: {}; aux_text_weight: {}; aux_image_weight: {}; aux_fusion_weight: {}; aux_schedule: {}; aux_schedule_start: {}; aux_schedule_end: {}; aux_label_mode: {}; aux_label_seed: {}; aux_random_label_seed: {}; aux_shuffle_seed: {}; aux_detach_features: {}; r5a_grad_mode: {}; uea_aux_mode: {}; uea_alpha_max: {}; regret_lambda: {}; route_balance_lambda: {}; regret_margin: {}; router_tau_start: {}; router_tau_end: {}; adapter_dim: {}; router_hidden: {}'.format(
            self.selector_mode, self.reliability_signal, self.reliability_lambda,
            self.reliability_gating, self.reliability_stats_mode,
            self.selection_margin_lambda, self.selection_margin,
            self.aux_loss_weight, self.aux_text_weight, self.aux_image_weight,
            self.aux_fusion_weight, self.aux_schedule, self.aux_schedule_start,
            self.aux_schedule_end, self.aux_label_mode, self.aux_label_seed,
            self.aux_random_label_seed, self.aux_shuffle_seed, self.aux_detach_features,
            self.r5a_grad_mode, self.uea_aux_mode, self.uea_alpha_max,
            self.regret_lambda, self.route_balance_lambda, self.regret_margin,
            self.router_tau_start, self.router_tau_end, self.adapter_dim, self.router_hidden))
        if self._uea_meta is not None:
            print('uea_meta: {}'.format(self._uea_meta))
        loss_fn = torch.nn.BCELoss()
        aux_loss_fn = torch.nn.BCELoss(reduction='none')
        optimizer = torch.optim.Adam(params=self.model.parameters(), lr=self.lr, weight_decay=self.weight_decay)
        scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=100, gamma=0.98)
        recorder = Recorder(self.early_stop)
        r5a_log_handle, r5a_writer = self._r5a_prepare_logger()
        r5a_groups = self._r5a_param_groups()
        if self.selector_mode == 'reliability' and self.reliability_stats_mode in ['prefit', 'pre_epoch']:
            self._fit_reliability_domain_stats()
        elif self.selector_mode == 'reliability':
            self.model.reset_reliability_stats()
        try:
            for epoch in range(self.epoches):
                self.model.train()
                if hasattr(self.model, 'set_regret_epoch'):
                    self.model.set_regret_epoch(epoch, self.epoches)
                if self.selector_mode == 'reliability' and self.reliability_stats_mode == 'online':
                    self.model.reset_reliability_stats()
                elif self.selector_mode == 'reliability' and self.reliability_stats_mode == 'pre_epoch':
                    self._fit_reliability_domain_stats()
                    self.model.train()
                train_data_iter = tqdm.tqdm(self.train_loader)
                steps_per_epoch = len(self.train_loader)
                avg_loss = Averager()
                for step_n, batch in enumerate(train_data_iter):
                    batch_data = clipdata2gpu(batch)
                    label = batch_data['label']

                    # The model now returns an additional loss_rec term
                    label0, text_fake_news, image_fake_news, fusion_fake_news, loss_rec = self.model(**batch_data)

                    # Main classification loss (L_cls)
                    loss0 = loss_fn(label0, label.float())

                    aux_label = self._aux_label_target(label)
                    aux_weights = self._current_aux_weights(epoch, step_n, steps_per_epoch)
                    if self.uea_aux_mode == 'none':
                        loss12 = loss_fn(text_fake_news, aux_label)
                        loss22 = loss_fn(image_fake_news, aux_label)
                        loss32 = loss_fn(fusion_fake_news, aux_label)
                        aux_losses = {
                            'text_branch': loss12,
                            'image_branch': loss22,
                            'fusion_branch': loss32,
                        }
                        aux_loss_term = self._weighted_aux_loss(aux_losses, aux_weights)
                    else:
                        aux_per_sample_losses = {
                            'text_branch': aux_loss_fn(text_fake_news, aux_label).view(-1),
                            'image_branch': aux_loss_fn(image_fake_news, aux_label).view(-1),
                            'fusion_branch': aux_loss_fn(fusion_fake_news, aux_label).view(-1),
                        }
                        aux_losses = {
                            branch: value.mean()
                            for branch, value in aux_per_sample_losses.items()
                        }
                        aux_loss_term = self._uea_weighted_aux_loss(
                            aux_per_sample_losses,
                            aux_weights,
                            batch_data.get('sample_id'),
                            label.device)
                    self._r5a_current_rec_loss = loss_rec

                    # Total loss computation L_total = L_cls + λ * L_rec
                    loss = loss0 + self.lambda_rec * loss_rec + aux_loss_term
                    margin_loss = self.model.selection_margin_loss()
                    if self.selection_margin_lambda > 0 and margin_loss is not None:
                        loss = loss + self.selection_margin_lambda * margin_loss
                    r3_regret_loss, r3_balance_loss = self.model.r3_losses()
                    if self.regret_lambda > 0 and r3_regret_loss is not None:
                        loss = loss + self.regret_lambda * r3_regret_loss
                    if self.route_balance_lambda > 0 and r3_balance_loss is not None:
                        loss = loss + self.route_balance_lambda * r3_balance_loss

                    self._r5a_backward(loss, loss0, aux_losses, aux_weights, optimizer, r5a_groups, epoch, step_n, r5a_writer)
                    optimizer.step()
                    if (scheduler is not None):
                        scheduler.step()
                    avg_loss.add(loss.item())
                print('Training Epoch {}; Loss {}; '.format(epoch + 1, avg_loss.item()))
                results0 = self.test(self.val_loader) # Validate on val_loader
                mark = recorder.add(results0)
                if mark == 'save':
                    torch.save(self.model.state_dict(),
                               os.path.join(self.save_param_dir, 'parameter_panda.pkl'))
                elif mark == 'esc':
                    break
                else:
                    continue
        finally:
            if r5a_log_handle is not None:
                r5a_log_handle.close()
        self.model.load_state_dict(torch.load(os.path.join(self.save_param_dir, 'parameter_panda.pkl')))
        if self.selector_mode == 'reliability':
            self._fit_reliability_domain_stats()
        if self.skip_final_test:
            results0 = self.test(self.val_loader)
            print("skip_final_test=True; returning final val result only: ", results0)
            return results0, os.path.join(self.save_param_dir, 'parameter_panda.pkl')
        print("开始进行最后的测试: ")
        results0 = self.test(self.test_loader)
        print("最后的结果", results0)

        return results0, os.path.join(self.save_param_dir, 'parameter_panda.pkl')

    def _fit_reliability_domain_stats(self):
        self.model.reset_reliability_stats()
        was_training = self.model.training
        self.model.eval()
        self.model.collect_reliability_stats = True
        data_iter = tqdm.tqdm(self.train_loader, desc='fit reliability domain stats')
        with torch.no_grad():
            for batch in data_iter:
                batch_data = clipdata2gpu(batch)
                self.model(**batch_data)
        self.model.collect_reliability_stats = False
        if was_training:
            self.model.train()
        else:
            self.model.eval()


    def test(self, dataloader):
        pred = []
        label = []
        category = []
        self.model.eval()
        data_iter = tqdm.tqdm(dataloader)
        for step_n, batch in enumerate(data_iter):
            with torch.no_grad():
                batch_data = clipdata2gpu(batch)
                batch_label = batch_data['label']
                batch_category = batch_data['category']

                # Adjust for the new model output signature
                batch_label_pred, _, _, _, _ = self.model(**batch_data)

                label.extend(batch_label.detach().cpu().numpy().tolist())
                pred.extend(batch_label_pred.detach().cpu().numpy().tolist())
                category.extend(batch_category.detach().cpu().numpy().tolist())

        metric_res = metricsTrueFalse(label, pred, category, self.category_dict)
        return metric_res
