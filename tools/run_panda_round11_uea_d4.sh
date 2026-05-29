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
OUT_ROOT="${OUT_ROOT:-repro_logs/round11_uea_d4/seed42}"
LOG_DIR="${LOG_DIR:-logs/round11_uea_d4}"
CKPT_ROOT="${CKPT_ROOT:-param_model/round11_uea_d4/seed42}"
UTILITY_CSV="${UTILITY_CSV:-repro_logs/round9_cue_d2/seed42/branch_utility_train.csv}"
CONTROL_SUMMARY="${CONTROL_SUMMARY:-repro_logs/round6_r6a_smoke/seed42/round6_r6a_smoke_summary.csv}"
CONTROL_EVAL_ROOT="${CONTROL_EVAL_ROOT:-repro_logs/round6_r6a_smoke/seed42/eval}"

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

cat > "$OUT_ROOT/round11_uea_d4_manifest.json" <<JSON
{
  "protocol_version": "round11_uea_d4_v1",
  "created_at": "$(date -Iseconds)",
  "status": "DRY_RUN_OR_RUNNING",
  "candidate_id": "Round11-A",
  "candidate_name": "UEA-PANDA utility-entropy anchored auxiliary allocation",
  "dataset": "$DATASET",
  "seed": $SEED,
  "model_name": "FTmodel",
  "allowed_splits": ["train", "val"],
  "test_split_exported": false,
  "test_used_for_decision": false,
  "utility_csv": "$UTILITY_CSV",
  "base_aux_loss_weight": 2.0,
  "variants": [
    "uea_entropy_alpha0p5",
    "uea_utility_only_alpha0p5",
    "uea_entropy_alpha0p25",
    "uea_utility_only_alpha0p25",
    "uea_shuffled_utility_entropy_alpha0p5",
    "uea_random_utility_entropy_alpha0p5",
    "uea_reverse_utility_entropy_alpha0p5",
    "uea_confidence_entropy_alpha0p5",
    "uea_boundary_entropy_alpha0p5"
  ],
  "reused_control_summary": "$CONTROL_SUMMARY",
  "reused_control_eval_root": "$CONTROL_EVAL_ROOT"
}
JSON

COMMON_ARGS=(
  --dataset "$DATASET"
  --model_name FTmodel
  --gpu "$GPU"
  --batchsize "$BATCH_SIZE"
  --lr "$LR"
  --epoch "$EPOCHS"
  --early_stop "$EARLY_STOP"
  --seed "$SEED"
  --num_workers "$NUM_WORKERS"
  --selector_mode deterministic_train
  --skip_final_test
  --aux_loss_weight 2.0
  --uea_utility_csv "$UTILITY_CSV"
)

variant_cmd() {
  local tag="$1"
  shift
  printf '%q ' "$PYTHON_BIN" main.py "${COMMON_ARGS[@]}" "$@" --save_param_dir "$CKPT_ROOT/$tag"
  echo
}

write_config() {
  local tag="$1"
  local family="$2"
  local mode="$3"
  local alpha="$4"
  local variant_dir="$OUT_ROOT/$tag"
  mkdir -p "$variant_dir"
  cat > "$variant_dir/variant_config.json" <<JSON
{
  "tag": "$tag",
  "family": "$family",
  "uea_aux_mode": "$mode",
  "uea_alpha_max": $alpha,
  "base_aux_loss_weight": 2.0,
  "utility_csv": "$UTILITY_CSV",
  "allowed_splits": ["train", "val"],
  "test_split_exported": false,
  "test_used_for_decision": false
}
JSON
}

run_variant() {
  local tag="$1"
  local family="$2"
  shift 2
  local ckpt_path="$CKPT_ROOT/$tag/FTmodel/parameter_panda.pkl"
  local train_log="$LOG_DIR/${DATASET}_seed${SEED}_${tag}_epoch${EPOCHS}.log"
  local variant_dir="$OUT_ROOT/$tag"
  local eval_ckpt_dir="$OUT_ROOT/eval/checkpoints_$tag"
  local eval_dir="$OUT_ROOT/eval/$tag"
  mkdir -p "$variant_dir" "$eval_ckpt_dir" "$eval_dir"

  {
    echo "# $tag"
    echo
    echo "Family: $family"
    echo "Dataset: $DATASET"
    echo "Seed: $SEED"
    echo "Epochs: $EPOCHS"
    echo "Created at: $(date -Iseconds)"
    echo
    echo "Command:"
    variant_cmd "$tag" "$@"
  } > "$variant_dir/notes.md"

  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[dry-run] $tag"
    variant_cmd "$tag" "$@"
    return
  fi

  if [[ -s "$ckpt_path" ]]; then
    echo "[$(date -Iseconds)] skip existing checkpoint: $tag"
  else
    echo "[$(date -Iseconds)] train: $tag"
    "$PYTHON_BIN" main.py "${COMMON_ARGS[@]}" "$@" \
      --save_param_dir "$CKPT_ROOT/$tag" \
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

write_config "uea_entropy_alpha0p5" "round11_uea_primary" "entropy" "0.5"
run_variant "uea_entropy_alpha0p5" "round11_uea_primary" --uea_aux_mode entropy --uea_alpha_max 0.5 --uea_seed "$SEED"

write_config "uea_utility_only_alpha0p5" "round11_uea_ablation" "utility_only" "0.5"
run_variant "uea_utility_only_alpha0p5" "round11_uea_ablation" --uea_aux_mode utility_only --uea_alpha_max 0.5 --uea_seed "$SEED"

write_config "uea_entropy_alpha0p25" "round11_uea_ablation" "entropy" "0.25"
run_variant "uea_entropy_alpha0p25" "round11_uea_ablation" --uea_aux_mode entropy --uea_alpha_max 0.25 --uea_seed "$SEED"

write_config "uea_utility_only_alpha0p25" "round11_uea_ablation" "utility_only" "0.25"
run_variant "uea_utility_only_alpha0p25" "round11_uea_ablation" --uea_aux_mode utility_only --uea_alpha_max 0.25 --uea_seed "$SEED"

write_config "uea_shuffled_utility_entropy_alpha0p5" "round11_uea_control" "shuffled_utility" "0.5"
run_variant "uea_shuffled_utility_entropy_alpha0p5" "round11_uea_control" --uea_aux_mode shuffled_utility --uea_alpha_max 0.5 --uea_seed "$((SEED + 101))"

write_config "uea_random_utility_entropy_alpha0p5" "round11_uea_control" "random_utility" "0.5"
run_variant "uea_random_utility_entropy_alpha0p5" "round11_uea_control" --uea_aux_mode random_utility --uea_alpha_max 0.5 --uea_seed "$((SEED + 202))"

write_config "uea_reverse_utility_entropy_alpha0p5" "round11_uea_control" "reverse_utility" "0.5"
run_variant "uea_reverse_utility_entropy_alpha0p5" "round11_uea_control" --uea_aux_mode reverse_utility --uea_alpha_max 0.5 --uea_seed "$SEED"

write_config "uea_confidence_entropy_alpha0p5" "round11_uea_control" "confidence" "0.5"
run_variant "uea_confidence_entropy_alpha0p5" "round11_uea_control" --uea_aux_mode confidence --uea_alpha_max 0.5 --uea_seed "$SEED"

write_config "uea_boundary_entropy_alpha0p5" "round10_boundary_negative_control" "boundary_entropy" "0.5"
run_variant "uea_boundary_entropy_alpha0p5" "round10_boundary_negative_control" --uea_aux_mode boundary_entropy --uea_alpha_max 0.5 --uea_seed "$SEED"

if [[ "$DRY_RUN" == "1" ]]; then
  exit 0
fi

"$PYTHON_BIN" tools/summarize_panda_round11_uea_d4.py \
  --uea-root "$OUT_ROOT" \
  --control-summary "$CONTROL_SUMMARY" \
  --control-eval-root "$CONTROL_EVAL_ROOT" \
  --utility-csv "$UTILITY_CSV" \
  --output-dir "$OUT_ROOT/summary" \
  --dataset "$DATASET" \
  --seed "$SEED"

"$PYTHON_BIN" - <<PY
import json
from pathlib import Path
path = Path("$OUT_ROOT/round11_uea_d4_manifest.json")
payload = json.loads(path.read_text(encoding="utf-8"))
payload["status"] = "COMPLETED"
path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY
