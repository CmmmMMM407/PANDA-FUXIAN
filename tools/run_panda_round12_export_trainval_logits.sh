#!/usr/bin/env bash
set -Eeuo pipefail

REPO_ROOT="${REPO_ROOT:-/root/autodl-tmp/panda_repro/panda}"
PYTHON_BIN="${PYTHON_BIN:-/root/miniconda3/bin/python}"
GPU="${GPU:-0}"
DATASET="${DATASET:-weibo21}"
SEEDS="${SEEDS:-42 2024 2026}"
BATCH_SIZE="${BATCH_SIZE:-32}"
NUM_WORKERS="${NUM_WORKERS:-0}"
OUT_ROOT="${OUT_ROOT:-repro_logs/round12_trainval_exports}"
LOG_DIR="${LOG_DIR:-logs/round12_trainval_exports}"

cd "$REPO_ROOT"
mkdir -p "$OUT_ROOT" "$LOG_DIR"

write_manifest() {
  local status="$1"
  cat > "$OUT_ROOT/round12_trainval_export_manifest.json" <<JSON
{
  "protocol_version": "round12_trainval_export_v1",
  "created_at": "$(date -Iseconds)",
  "status": "$status",
  "dataset": "$DATASET",
  "seeds": "$SEEDS",
  "allowed_splits": ["train", "val"],
  "test_split_exported": false,
  "test_used_for_decision": false,
  "families": ["panda_reproduced", "static_aux_2p0", "generic_dwa"],
  "notes": [
    "Exports only selector_variant train/val CSVs from saved checkpoints.",
    "No sample content, image paths, checkpoint weights, or test predictions are copied into the output CSVs."
  ]
}
JSON
}

link_ckpt() {
  local family="$1"
  local seed="$2"
  local source="$3"
  local ckpt_dir="$OUT_ROOT/checkpoints_${family}"
  mkdir -p "$ckpt_dir"
  if [[ ! -s "$source" ]]; then
    echo "Missing checkpoint for ${family} seed${seed}: ${source}" >&2
    return 1
  fi
  ln -sfn "$(realpath "$source")" "$ckpt_dir/${DATASET}_seed${seed}_parameter_panda.pkl"
}

prepare_family_checkpoints() {
  local family="$1"
  local seed
  for seed in $SEEDS; do
    case "$family:$seed" in
      panda_reproduced:*)
        link_ckpt "$family" "$seed" "param_model/FTmodel/checkpoints_by_seed/${DATASET}_seed${seed}_parameter_panda.pkl"
        ;;
      static_aux_2p0:42)
        link_ckpt "$family" "$seed" "param_model/round6_r6a_smoke/static_aux_weight_2p0_anchor_control/FTmodel/parameter_panda.pkl"
        ;;
      static_aux_2p0:2024|static_aux_2p0:2026)
        link_ckpt "$family" "$seed" "param_model/round8_r8b_d5_seed_recheck/seed${seed}/static_aux_weight_2p0_anchor_control/FTmodel/parameter_panda.pkl"
        ;;
      generic_dwa:42)
        link_ckpt "$family" "$seed" "param_model/round6_r6a_smoke/generic_dwa/FTmodel/parameter_panda.pkl"
        ;;
      generic_dwa:2024|generic_dwa:2026)
        link_ckpt "$family" "$seed" "param_model/round8_r8b_d5_seed_recheck/seed${seed}/generic_dwa/FTmodel/parameter_panda.pkl"
        ;;
      *)
        echo "Unsupported family/seed: ${family}/${seed}" >&2
        return 1
        ;;
    esac
  done
}

run_export() {
  local family="$1"
  local mode="$2"
  local family_out="$OUT_ROOT/${family}"
  local ckpt_dir="$OUT_ROOT/checkpoints_${family}"
  mkdir -p "$family_out"
  echo "[$(date -Iseconds)] export ${family} mode=${mode}"
  "$PYTHON_BIN" tools/evaluate_panda_selector_variants.py \
    --datasets "$DATASET" \
    --seeds $SEEDS \
    --splits train val \
    --modes "$mode" \
    --batch-size "$BATCH_SIZE" \
    --num-workers "$NUM_WORKERS" \
    --gpu "$GPU" \
    --checkpoint-dir "$ckpt_dir" \
    --output-dir "$family_out" \
    --overwrite \
    > "$LOG_DIR/${DATASET}_${family}_trainval_export.log" 2>&1
}

write_manifest "RUNNING"

prepare_family_checkpoints panda_reproduced
prepare_family_checkpoints static_aux_2p0
prepare_family_checkpoints generic_dwa

run_export panda_reproduced panda_gumbel
run_export static_aux_2p0 deterministic_train
run_export generic_dwa deterministic_train

write_manifest "COMPLETED"
