#!/usr/bin/env python3
"""Round13 ADWA-PANDA D3.5 gradient sanity.

Train-only check: no optimizer step, no checkpoint, no val/test access.
It verifies that ADWA-PANDA keeps final CE gradients on the final boundary
while branch-relative auxiliary supervision reaches branch features and aux
heads with finite, nonzero gradients.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from model.PANDA import MultiDomainPLEFENDModel
from utils.utils import clipdata2gpu
from utils.weibo21_clip_prompt import bert_data as weibo21_data


EPS = 1e-8
WEIBO21_CATEGORY_DICT = {
    "科技": 0,
    "军事": 1,
    "教育考试": 2,
    "灾难事故": 3,
    "政治": 4,
    "医药健康": 5,
    "财经商业": 6,
    "文体娱乐": 7,
    "社会生活": 8,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", default="weibo21", choices=["weibo21"])
    parser.add_argument("--model-name", "--model_name", dest="model_name", default="FTmodel", choices=["FTmodel"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--gpu", default="0")
    parser.add_argument("--batchsize", type=int, default=8)
    parser.add_argument("--max-batches", type=int, default=5)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--max-len", type=int, default=197)
    parser.add_argument("--bert-vocab-file", default="./pretrained_model/chinese_roberta_wwm_base_ext_pytorch/vocab.txt")
    parser.add_argument("--bert", default="./pretrained_model/chinese_roberta_wwm_base_ext_pytorch")
    parser.add_argument("--checkpoint", default="./param_model/FTmodel/checkpoints_by_seed/weibo21_seed42_parameter_panda.pkl")
    parser.add_argument("--output-dir", default="repro_logs/round13_adwa_d35_gradient_sanity/seed42")
    parser.add_argument("--lambda-aux", type=float, default=2.0)
    parser.add_argument("--adwa-tau", type=float, default=2.0)
    parser.add_argument("--adwa-clip-min", type=float, default=0.5)
    parser.add_argument("--adwa-clip-max", type=float, default=1.25)
    parser.add_argument("--adwa-final-guard-ratio", type=float, default=1.05)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


def clean_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): clean_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_json(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean_json(value.tolist())
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, (np.floating, float)):
        value = float(value)
        return value if math.isfinite(value) else None
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean_json(payload), indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")


def flatten_grads(grads: list[torch.Tensor | None]) -> torch.Tensor | None:
    pieces = [grad.detach().reshape(-1).float() for grad in grads if grad is not None]
    return None if not pieces else torch.cat(pieces)


def grad_norm(flat: torch.Tensor | None) -> float:
    if flat is None or flat.numel() == 0:
        return 0.0
    return float(torch.norm(flat).detach().cpu())


def grad_cosine(flat: torch.Tensor | None, ref: torch.Tensor | None) -> float | None:
    if flat is None or ref is None or flat.numel() == 0 or ref.numel() == 0:
        return None
    denom = torch.norm(flat) * torch.norm(ref)
    if float(denom.detach().cpu()) < EPS:
        return None
    return float((torch.dot(flat, ref) / denom.clamp_min(EPS)).detach().cpu())


def finite_tensor(value: torch.Tensor) -> bool:
    return bool(torch.isfinite(value.detach()).all().item())


class ForwardCapture:
    def __init__(self, module: torch.nn.Module):
        self.h_final = None
        self.final_logits = None
        self._pre = module.register_forward_pre_hook(self._capture_input)
        self._post = module.register_forward_hook(self._capture_output)

    def _capture_input(self, _module, inputs) -> None:
        self.h_final = inputs[0]

    def _capture_output(self, _module, _inputs, output) -> None:
        self.final_logits = output.squeeze(1) if output.dim() == 2 and output.size(1) == 1 else output

    def close(self) -> None:
        self._pre.remove()
        self._post.remove()


def build_model(args: argparse.Namespace):
    model = MultiDomainPLEFENDModel(
        emb_dim=768,
        mlp_dims=[384],
        bert=args.bert,
        out_channels=320,
        dropout=0.2,
        domain_num=9,
        selector_mode="deterministic_train",
        reliability_signal="branch_fusion",
        reliability_lambda=0.0,
    )
    state = torch.load(args.checkpoint, map_location="cpu")
    missing, unexpected = model.load_state_dict(state, strict=False)
    model.cuda()
    model.train()
    return model, [str(item) for item in missing], [str(item) for item in unexpected]


def build_train_loader(args: argparse.Namespace):
    loader = weibo21_data(
        max_len=args.max_len,
        batch_size=args.batchsize,
        vocab_file=args.bert_vocab_file,
        category_dict=WEIBO21_CATEGORY_DICT,
        num_workers=args.num_workers,
    )
    return loader.load_data(
        "./Weibo_21/train_datasets.xlsx",
        "Weibo_21/train_loader.pkl",
        "Weibo_21/train_clip_loader.pkl",
        True,
    )


def unique_trainable_params(modules: list[torch.nn.Module]) -> list[torch.nn.Parameter]:
    seen = set()
    params = []
    for module in modules:
        for param in module.parameters():
            if param.requires_grad and id(param) not in seen:
                seen.add(id(param))
                params.append(param)
    return params


def param_groups(model: MultiDomainPLEFENDModel) -> dict[str, list[torch.nn.Parameter]]:
    return {
        "final_classifier": unique_trainable_params([model.final_classifier_panda]),
        "text_branch": unique_trainable_params([model.text_experts, model.text_share_expert, model.att_mlp_text]),
        "image_branch": unique_trainable_params([model.image_experts, model.image_share_expert, model.att_mlp_img]),
        "fusion_branch": unique_trainable_params([
            model.fusion_experts,
            model.fusion_share_expert,
            model.fusion_gate_list0,
            model.domain_fusion,
            model.MLP_fusion,
            model.att_mlp_mm,
        ]),
        "text_aux_head": unique_trainable_params([model.text_classifier]),
        "image_aux_head": unique_trainable_params([model.image_classifier]),
        "fusion_aux_head": unique_trainable_params([model.fusion_classifier]),
    }


def collect_refs(loss: torch.Tensor, groups: dict[str, list[torch.nn.Parameter]], h_final: torch.Tensor):
    refs = {}
    params = []
    slices = {}
    cursor = 0
    for name, group in groups.items():
        slices[name] = (cursor, cursor + len(group))
        params.extend(group)
        cursor += len(group)
    grads = torch.autograd.grad(loss, params + [h_final], retain_graph=True, allow_unused=True)
    param_grads = list(grads[:-1])
    refs["h_final"] = flatten_grads([grads[-1]])
    for name, (lo, hi) in slices.items():
        refs[name] = flatten_grads(param_grads[lo:hi])
    return refs, params, slices


def weighted_aux_loss(aux_losses: dict[str, torch.Tensor], weights: dict[str, float]) -> torch.Tensor:
    return (
        weights["text_branch"] * aux_losses["text_branch"]
        + weights["image_branch"] * aux_losses["image_branch"]
        + weights["fusion_branch"] * aux_losses["fusion_branch"]
    ) / 3.0


def adwa_weights(
    current_aux: torch.Tensor,
    current_final: torch.Tensor,
    prev_aux: torch.Tensor | None,
    prev_final: torch.Tensor | None,
    args: argparse.Namespace,
):
    reason = None
    if prev_aux is None or prev_final is None:
        reason = "warmup_no_previous_loss"
    elif not bool(torch.isfinite(current_aux).all()) or not bool(torch.isfinite(current_final)):
        reason = "nonfinite_loss"
    elif float(current_final.cpu()) > float(prev_final.cpu()) * float(args.adwa_final_guard_ratio):
        reason = "final_loss_guard"
    if reason is None:
        ratio = current_aux / prev_aux.clamp_min(EPS)
        raw = torch.softmax(ratio / max(float(args.adwa_tau), EPS), dim=0) * 3.0
        raw = torch.clamp(raw, min=float(args.adwa_clip_min), max=float(args.adwa_clip_max))
        raw = raw / raw.mean().clamp_min(EPS)
    else:
        raw = torch.ones_like(current_aux)
    values = raw.detach().cpu().tolist()
    return {
        "text_branch": float(args.lambda_aux) * float(values[0]),
        "image_branch": float(args.lambda_aux) * float(values[1]),
        "fusion_branch": float(args.lambda_aux) * float(values[2]),
    }, {
        "guard_active": reason is not None,
        "guard_reason": reason or "none",
        "raw_text_weight": float(values[0]),
        "raw_image_weight": float(values[1]),
        "raw_fusion_weight": float(values[2]),
    }


def grad_record(
    batch_idx: int,
    loss_name: str,
    loss: torch.Tensor,
    refs: dict[str, torch.Tensor | None],
    groups: dict[str, list[torch.nn.Parameter]],
    h_final: torch.Tensor,
    diag: dict,
):
    params = []
    slices = {}
    cursor = 0
    for name, group in groups.items():
        slices[name] = (cursor, cursor + len(group))
        params.extend(group)
        cursor += len(group)
    grads = torch.autograd.grad(loss, params + [h_final], retain_graph=True, allow_unused=True)
    param_grads = list(grads[:-1])
    h_flat = flatten_grads([grads[-1]])
    row = {
        "batch_idx": batch_idx,
        "candidate_id": "Round13-ADWA-PANDA",
        "loss_name": loss_name,
        "loss_value": float(loss.detach().cpu()),
        "loss_finite": finite_tensor(loss),
        "h_final_grad_norm": grad_norm(h_flat),
        "h_final_cosine_vs_final_ce": grad_cosine(h_flat, refs.get("h_final")),
        "has_nonzero_h_final_grad": bool(h_flat is not None and float(torch.norm(h_flat).cpu()) > 1e-10),
    }
    row.update(diag)
    for group_name, (lo, hi) in slices.items():
        flat = flatten_grads(param_grads[lo:hi])
        row[f"{group_name}_grad_norm"] = grad_norm(flat)
        row[f"{group_name}_cosine_vs_final_ce"] = grad_cosine(flat, refs.get(group_name))
        row[f"has_nonzero_{group_name}_grad"] = bool(flat is not None and float(torch.norm(flat).cpu()) > 1e-10)
    return row


def summarize(records: list[dict]) -> dict:
    summary = {}
    for loss_name in sorted({row["loss_name"] for row in records}):
        subset = [row for row in records if row["loss_name"] == loss_name]
        out = {"rows": len(subset)}
        for key, value in subset[0].items():
            if isinstance(value, bool):
                out[f"rate_{key}"] = float(np.mean([bool(row[key]) for row in subset]))
            elif isinstance(value, (int, float)) and key != "batch_idx":
                vals = [float(row[key]) for row in subset if isinstance(row.get(key), (int, float)) and math.isfinite(float(row[key]))]
                out[f"mean_{key}"] = float(np.mean(vals)) if vals else None
        summary[loss_name] = out
    return summary


def decide(summary: dict) -> dict:
    adwa = summary.get("adwa_panda")
    reasons = []
    if not adwa:
        reasons.append("missing_adwa_records")
    else:
        for key in [
            "rate_loss_finite",
            "rate_has_nonzero_h_final_grad",
            "rate_has_nonzero_final_classifier_grad",
            "rate_has_nonzero_text_branch_grad",
            "rate_has_nonzero_image_branch_grad",
            "rate_has_nonzero_fusion_branch_grad",
            "rate_has_nonzero_text_aux_head_grad",
            "rate_has_nonzero_image_aux_head_grad",
            "rate_has_nonzero_fusion_aux_head_grad",
        ]:
            if float(adwa.get(key, 0.0)) < 1.0:
                reasons.append(f"adwa_{key}_lt_1")
    status = "D3.5-Feasible-A" if not reasons else "D3.5-No-Go-for-current-ADWA-gradient"
    return {
        "status": status,
        "claim_scope": "ADWA-PANDA D3.5 train-only gradient reachability",
        "level_reached": "D3.5",
        "required_level_for_training_implementation": "D4 seed42 train/val-only",
        "required_level_for_stability": "D5 three-seed val",
        "reasons": reasons,
        "training_allowed_next": not reasons,
        "test_split_exported": False,
        "test_used_for_decision": False,
    }


def initial_manifest(args: argparse.Namespace) -> dict:
    return {
        "protocol_version": "round13_adwa_d35_gradient_sanity_v1",
        "candidate_id": "Round13-ADWA-PANDA",
        "dataset": args.dataset,
        "seed": args.seed,
        "model_name": args.model_name,
        "checkpoint": args.checkpoint,
        "allowed_splits": ["train"],
        "forbidden_splits": ["val", "test"],
        "test_split_exported": False,
        "test_used_for_decision": False,
        "optimization_steps": 0,
        "checkpoint_written": False,
        "variants": ["final_ce", "static_aux_2p0", "generic_dwa_proxy", "detached_aux_control", "adwa_panda"],
    }


def write_markdown(path: Path, payload: dict) -> None:
    lines = [
        "# Round13 ADWA-PANDA D3.5 Gradient Sanity",
        "",
        "Scope: Weibo-21 seed42 train-only real PANDA batches. No optimizer step, no checkpoint, no val/test.",
        "",
        f"- Decision: `{payload['decision']['status']}`",
        f"- Observed batches: `{payload['observed_batches']}`",
        f"- Test split exported: `{str(payload['test_split_exported']).lower()}`",
        f"- Test used for decision: `{str(payload['test_used_for_decision']).lower()}`",
        "",
        "## Loss Means",
        "",
    ]
    for key, row in payload["summary"].items():
        lines.append(f"### {key}")
        for field in [
            "mean_loss_value",
            "mean_h_final_grad_norm",
            "mean_final_classifier_grad_norm",
            "mean_text_branch_grad_norm",
            "mean_image_branch_grad_norm",
            "mean_fusion_branch_grad_norm",
            "mean_text_aux_head_grad_norm",
            "mean_image_aux_head_grad_norm",
            "mean_fusion_aux_head_grad_norm",
            "mean_raw_text_weight",
            "mean_raw_image_weight",
            "mean_raw_fusion_weight",
            "rate_guard_active",
        ]:
            if field in row:
                lines.append(f"- {field}: `{row[field]}`")
        lines.append("")
    if payload["decision"].get("reasons"):
        lines.extend(["## Reasons", ""])
        lines.extend(f"- {reason}" for reason in payload["decision"]["reasons"])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    os.environ["CUDA_VISIBLE_DEVICES"] = args.gpu
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = initial_manifest(args)
    write_json(output_dir / "round13_adwa_d35_manifest.json", manifest)
    if args.dry_run:
        print(json.dumps(clean_json(manifest), ensure_ascii=False, indent=2, allow_nan=False))
        return 0

    set_seed(args.seed)
    model, missing, unexpected = build_model(args)
    train_loader = build_train_loader(args)
    groups = param_groups(model)
    capture = ForwardCapture(model.final_classifier_panda)
    records = []
    prev_aux = None
    prev_final = None
    observed_batches = 0
    try:
        for batch_idx, batch in enumerate(train_loader):
            if batch_idx >= args.max_batches:
                break
            model.zero_grad(set_to_none=True)
            batch_data = clipdata2gpu(batch)
            label = batch_data["label"].float()
            final_prob, text_prob, image_prob, fusion_prob, rec_loss = model(**batch_data)
            h_final = capture.h_final
            final_logits = capture.final_logits
            if h_final is None or final_logits is None:
                raise RuntimeError("Failed to capture h_final/final logits from final_classifier_panda")
            final_ce = F.binary_cross_entropy_with_logits(final_logits, label)
            aux_losses = {
                "text_branch": F.binary_cross_entropy(text_prob, label),
                "image_branch": F.binary_cross_entropy(image_prob, label),
                "fusion_branch": F.binary_cross_entropy(fusion_prob, label),
            }
            refs, _, _ = collect_refs(final_ce, groups, h_final)
            static_weights = {key: float(args.lambda_aux) for key in aux_losses}
            static_aux = weighted_aux_loss(aux_losses, static_weights)
            current_aux = torch.stack([aux_losses["text_branch"].detach(), aux_losses["image_branch"].detach(), aux_losses["fusion_branch"].detach()]).float()
            adwa, adwa_diag = adwa_weights(current_aux, final_ce.detach().float(), prev_aux, prev_final, args)
            adwa_aux = weighted_aux_loss(aux_losses, adwa)
            generic_stack = torch.stack([final_ce.detach(), current_aux[0], current_aux[1], current_aux[2]])
            generic_weights = torch.softmax(generic_stack / 2.0, dim=0) * 4.0
            generic_loss = sum(
                float(weight.detach().cpu()) * loss
                for weight, loss in zip(generic_weights, [final_ce, aux_losses["text_branch"], aux_losses["image_branch"], aux_losses["fusion_branch"]])
            ) / 4.0
            detached_aux = weighted_aux_loss(
                {
                    "text_branch": F.binary_cross_entropy(text_prob.detach(), label),
                    "image_branch": F.binary_cross_entropy(image_prob.detach(), label),
                    "fusion_branch": F.binary_cross_entropy(fusion_prob.detach(), label),
                },
                static_weights,
            )
            losses = [
                ("final_ce", final_ce, {}),
                ("static_aux_2p0", final_ce + rec_loss + static_aux, {}),
                ("generic_dwa_proxy", generic_loss + rec_loss, {}),
                ("detached_aux_control", final_ce + rec_loss + detached_aux, {}),
                ("adwa_panda", final_ce + rec_loss + adwa_aux, adwa_diag),
            ]
            for name, loss, diag in losses:
                records.append(grad_record(batch_idx, name, loss, refs, groups, h_final, diag))
            prev_aux = current_aux.detach()
            prev_final = final_ce.detach().float()
            observed_batches += 1
            torch.cuda.empty_cache()
    finally:
        capture.close()

    csv_path = output_dir / "round13_adwa_d35_gradient_records.csv"
    fieldnames = sorted({key for row in records for key in row.keys()}) if records else ["batch_idx", "loss_name"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    summary = summarize(records)
    decision = decide(summary)
    manifest["status"] = "COMPLETED" if records else "BLOCKED"
    manifest["missing_state_keys"] = missing
    manifest["unexpected_state_keys"] = unexpected
    payload = {
        "task": "round13_adwa_d35_gradient_sanity",
        "status": manifest["status"],
        "config": vars(args),
        "observed_batches": observed_batches,
        "allowed_splits": ["train"],
        "test_split_exported": False,
        "test_used_for_decision": False,
        "optimization_steps": 0,
        "checkpoint_written": False,
        "manifest": manifest,
        "summary": summary,
        "decision": decision,
        "records_csv": str(csv_path),
    }
    write_json(output_dir / "round13_adwa_d35_manifest.json", manifest)
    write_json(output_dir / "round13_adwa_d35_summary.json", payload)
    write_json(output_dir / "round13_adwa_d35_decision_summary.json", decision)
    write_markdown(output_dir / "round13_adwa_d35_summary.md", payload)
    print(json.dumps(clean_json(decision), ensure_ascii=False, indent=2, allow_nan=False))
    return 0 if records else 2


if __name__ == "__main__":
    raise SystemExit(main())
