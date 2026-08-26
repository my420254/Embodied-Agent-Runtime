#!/usr/bin/env bash
set -u

cd /data/zmy/OurAgent-he1 || exit 1

LOG_ROOT="/data/zmy/OurAgent-he1/benchmark/framework_experiment_records/full_queue_20260806"
mkdir -p "$LOG_ROOT"

run_step() {
  local name="$1"
  shift
  local log_file="$LOG_ROOT/${name}.log"
  echo "===== START ${name} $(date -u '+%Y-%m-%d %H:%M:%S UTC') =====" | tee -a "$LOG_ROOT/queue.log"
  echo "CMD: $*" | tee -a "$LOG_ROOT/queue.log"
  "$@" 2>&1 | tee "$log_file"
  local status=${PIPESTATUS[0]}
  echo "===== END ${name} status=${status} $(date -u '+%Y-%m-%d %H:%M:%S UTC') =====" | tee -a "$LOG_ROOT/queue.log"
  return "$status"
}

run_step eai_behavior_full_20260806_todo_hooks \
  python benchmark/eai/behavior/framework/code/run.py \
    --run-name eai_behavior_full_20260806_todo_hooks \
    --expected-count 100 \
    --workers 1 \
    --launch-shards 1 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key

run_step eai_virtualhome_full_20260806_todo_hooks \
  python benchmark/eai/virtualhome/framework/code/run.py \
    --run-name eai_virtualhome_full_20260806_todo_hooks \
    --expected-count 342 \
    --workers 1 \
    --launch-shards 1 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key

run_step reactree_wah_full_20260806_todo_hooks \
  python benchmark/reactree/wah/framework/code/run.py \
    --run-name reactree_wah_full_20260806_todo_hooks \
    --expected-count 100 \
    --workers 1 \
    --launch-shards 1 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --eval-mode official \
    --official-port-ids 26

run_step reactree_alfred_seen_full_20260806_todo_hooks \
  python benchmark/reactree/alfred/framework/code/run.py \
    --run-name reactree_alfred_seen_full_20260806_todo_hooks \
    --eval-set valid_seen \
    --expected-count 820 \
    --workers 1 \
    --launch-shards 1 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --x-display 71
