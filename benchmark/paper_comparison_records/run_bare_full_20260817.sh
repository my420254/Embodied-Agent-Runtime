#!/usr/bin/env bash
set -u

cd /data/zmy/OurAgent-he1 || exit 1

export PYTHONUNBUFFERED=1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy

PYBIN="/data/zmy/envs/ouragent/bin/python"
LOG_ROOT="/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs"
mkdir -p "${LOG_ROOT}"

run_step() {
  local name="$1"
  shift
  local log_file="${LOG_ROOT}/${name}.log"
  {
    echo "===== START ${name} $(date -u '+%Y-%m-%d %H:%M:%S UTC') ====="
    echo "CMD: $*"
    "$@"
    local status=$?
    echo "===== END ${name} status=${status} $(date -u '+%Y-%m-%d %H:%M:%S UTC') ====="
    return "${status}"
  } 2>&1 | tee "${log_file}"
  return "${PIPESTATUS[0]}"
}

run_step delta_bare_full_qwen35_20260817 \
  "${PYBIN}" benchmark/delta/bare_baseline/code/run.py \
    --run-name delta_bare_full_qwen35_20260817 \
    --workers 5 \
    --ports 18004 \
    --api-model Qwen3.5-9B \
    --api-key qwen-local-key

run_step eai_behavior_bare_full_qwen36_20260817 \
  "${PYBIN}" benchmark/eai/behavior/bare_baseline/code/run.py \
    --run-name eai_behavior_bare_full_qwen36_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key

run_step eai_virtualhome_bare_full_qwen36_valid_20260817 \
  "${PYBIN}" benchmark/eai/virtualhome/bare_baseline/code/run.py \
    --run-name eai_virtualhome_bare_full_qwen36_valid_20260817 \
    --valid-only \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key

run_step reactree_wah_bare_full_qwen36_official_20260817 \
  "${PYBIN}" benchmark/reactree/wah/bare_baseline/code/run.py \
    --run-name reactree_wah_bare_full_qwen36_official_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --official-base-port 9900 \
    --official-port-ids 0 1 2 3 4 \
    --official-timeout-s 180 \
    --full-observable

run_step reactree_alfred_bare_full_qwen35_18004_seen_20260817 \
  /data/zmy/alfred/bare_baseline/run_bare_18004.sh \
    --split valid_seen \
    --all-cases \
    --run-name reactree_alfred_bare_full_qwen35_18004_seen_20260817 \
    --reset

echo "===== ALL DONE $(date -u '+%Y-%m-%d %H:%M:%S UTC') =====" | tee -a "${LOG_ROOT}/queue.log"
