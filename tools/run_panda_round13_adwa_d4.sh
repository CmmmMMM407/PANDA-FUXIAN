#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="${REPO_ROOT:-/root/autodl-tmp/panda_repro/panda}"
PYTHON_BIN="${PYTHON_BIN:-/root/miniconda3/bin/python}"
GPU="${GPU:-0}"
DATASET="${DATASET:-weibo21}"
SEED="${SEED:-42}"
EPOCHS="${EPOCHS:-5}"
EARLY_STOP="${EARLY_STOP:-6}"
BATCH_SIZE="${BATCH_SIZE:-32}"
LR="${LR:-1e-4}"
NUM_WORKERS="${NUM_WORKERS:-0}"
OUT_ROOT="${OUT_ROOT:-repro_logs/round13_adwa_d4/seed${SEED}}"
LOG_DIR="${LOG_DIR:-logs/round13_adwa_d4}"
CKPT_ROOT="${CKPT_ROOT:-param_model/round13_adwa_d4/seed${SEED}}"

DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=1
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

cd "$REPO_ROOT"
mkdir -p "$OUT_ROOT" "$LOG_DIR" "$CKPT_ROOT"

cat > "$OUT_ROOT/round13_adwa_d4_manifest.json" <<JSON
{
  "protocol_version": "round13_adwa_d4_v1",
  "created_at": "$(date -Iseconds)",
  "status": "DRY_RUN_OR_RUNNING",
  "candidate_id": "Round13-ADWA-PANDA",
  "dataset": "$DATASET",
  "seed": $SEED,
  "model_name": "FTmodel",
  "allowed_splits": ["train", "val"],
  "test_split_exported": false,
  "test_used_for_decision": false,
  "variants": [
    "deterministic_train_l0",
    "static_aux_weight_2p0_anchor_control",
    "generic_dwa",
    "generic_gradnorm",
    "generic_pcgrad",
    "generic_cagrad",
    "detached_aux_no_feature_update",
    "same_budget_noop_l0",
    "adwa_clip_1p5_2p5",
    "adwa_clip_1p0_2p5",
    "adwa_final_guard",
    "adwa_entropy_smoothed_proxy"
  ]
}
JSON

run_variant() {
  local tag="$1"
  shift
  local variant_dir="$OUT_ROOT/$tag"
  local eval_root="$OUT_ROOT/eval"
  local eval_ckpt_dir="$eval_root/checkpoints_${tag}"
  local eval_dir="$eval_root/${tag}"
  local ckpt_path="$CKPT_ROOT/${tag}/FTmodel/parameter_panda.pkl"
  local train_log="$LOG_DIR/${DATASET}_seed${SEED}_${tag}_epoch${EPOCHS}.log"
  mkdir -p "$variant_dir" "$eval_ckpt_dir" "$eval_dir"

  {
    echo "# $tag"
    echo
    echo "Dataset: $DATASET"
    echo "Seed: $SEED"
    echo "Allowed splits: train,val"
    echo "Test used for decision: false"
    echo
    echo "Command:"
    printf "%q " "$PYTHON_BIN" main.py \
      --dataset "$DATASET" \
      --model_name FTmodel \
      --gpu "$GPU" \
      --batchsize "$BATCH_SIZE" \
      --lr "$LR" \
      --epoch "$EPOCHS" \
      --early_stop "$EARLY_STOP" \
      --seed "$SEED" \
      --num_workers "$NUM_WORKERS" \
      --selector_mode deterministic_train \
      --skip_final_test \
      "$@" \
      --save_param_dir "$CKPT_ROOT/${tag}" \
      --r5a_log_dir "$variant_dir"
    echo
  } > "$variant_dir/notes.md"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] $tag"
    sed -n '/^Command:$/,$p' "$variant_dir/notes.md" | tail -1
    return
  fi

  if [[ -s "$ckpt_path" ]]; then
    echo "[$(date -Iseconds)] skip existing checkpoint: $tag"
  else
    echo "[$(date -Iseconds)] train: $tag"
    "$PYTHON_BIN" main.py \
      --dataset "$DATASET" \
      --model_name FTmodel \
      --gpu "$GPU" \
      --batchsize "$BATCH_SIZE" \
      --lr "$LR" \
      --epoch "$EPOCHS" \
      --early_stop "$EARLY_STOP" \
      --seed "$SEED" \
      --num_workers "$NUM_WORKERS" \
      --selector_mode deterministic_train \
      --skip_final_test \
      "$@" \
      --save_param_dir "$CKPT_ROOT/${tag}" \
      --r5a_log_dir "$variant_dir" \
      > "$train_log" 2>&1
  fi

  if [[ ! -s "$ckpt_path" ]]; then
    echo "Missing checkpoint after training: $ckpt_path" >&2
    return 1
  fi
  ln -sfn "$(realpath "$ckpt_path")" "$eval_ckpt_dir/${DATASET}_seed${SEED}_parameter_panda.pkl"
  "$PYTHON_BIN" tools/evaluate_panda_selector_variants.py \
    --datasets "$DATASET" \
    --seeds "$SEED" \
    --splits val \
    --modes deterministic_train \
    --batch-size "$BATCH_SIZE" \
    --num-workers "$NUM_WORKERS" \
    --gpu "$GPU" \
    --checkpoint-dir "$eval_ckpt_dir" \
    --output-dir "$eval_dir" \
    --overwrite \
    > "$LOG_DIR/${DATASET}_seed${SEED}_${tag}_eval.log" 2>&1
}

run_variant deterministic_train_l0 --aux_loss_weight 0.0 --r5a_grad_mode none
run_variant static_aux_weight_2p0_anchor_control --aux_loss_weight 2.0 --r5a_grad_mode none
run_variant generic_dwa --aux_loss_weight 1.0 --r5a_grad_mode generic_dwa
run_variant generic_gradnorm --aux_loss_weight 1.0 --r5a_grad_mode generic_gradnorm
run_variant generic_pcgrad --aux_loss_weight 1.0 --r5a_grad_mode generic_pcgrad
run_variant generic_cagrad --aux_loss_weight 1.0 --r5a_grad_mode generic_cagrad
run_variant detached_aux_no_feature_update --aux_loss_weight 2.0 --r5a_grad_mode none --aux_detach_features
run_variant same_budget_noop_l0 --aux_loss_weight 0.0 --r5a_grad_mode same_budget_noop
run_variant adwa_clip_1p5_2p5 --lambda_aux 2.0 --r5a_grad_mode adwa_panda --adwa_clip_min 0.75 --adwa_clip_max 1.25 --adwa_tau 2.0
run_variant adwa_clip_1p0_2p5 --lambda_aux 2.0 --r5a_grad_mode adwa_panda --adwa_clip_min 0.5 --adwa_clip_max 1.25 --adwa_tau 2.0
run_variant adwa_final_guard --lambda_aux 2.0 --r5a_grad_mode adwa_panda --adwa_clip_min 0.5 --adwa_clip_max 1.25 --adwa_tau 2.0 --adwa_final_guard_ratio 1.02
run_variant adwa_entropy_smoothed_proxy --lambda_aux 2.0 --r5a_grad_mode adwa_panda --adwa_clip_min 0.75 --adwa_clip_max 1.10 --adwa_tau 3.0

if [[ "$DRY_RUN" == "1" ]]; then
  exit 0
fi

"$PYTHON_BIN" - <<PY
import json
from pathlib import Path
path = Path("$OUT_ROOT/round13_adwa_d4_manifest.json")
payload = json.loads(path.read_text(encoding="utf-8"))
payload["status"] = "COMPLETED_TRAIN_VAL_ONLY"
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
PY
