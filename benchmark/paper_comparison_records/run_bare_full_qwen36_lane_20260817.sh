#!/usr/bin/env bash
set -u

cd /data/zmy/OurAgent-he1 || exit 1

export PYTHONUNBUFFERED=1
export OURAGENT_WORKSPACE_ROOT=/data/zmy
unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy

PYBIN="/data/zmy/envs/ouragent/bin/python"
LOG_ROOT="/data/zmy/OurAgent-he1/benchmark/paper_comparison_records/bare_full_20260817/logs_lanes/qwen36"
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

require_model() {
  local port="$1"
  local expected="$2"
  local actual
  actual="$(curl --noproxy '*' -sS -m 10 "http://192.168.27.250:${port}/v1/models" \
    -H 'Authorization: Bearer qwen-local-key' \
    | jq -r '.data[]?.id' | head -n 1)"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "ERROR: port ${port} expected ${expected}, got ${actual:-<empty>}" >&2
    return 1
  fi
  echo "OK: port ${port} -> ${actual}"
}

require_free_ports() {
  local label="$1"
  shift
  local busy=""
  local port
  for port in "$@"; do
    if ss -ltnH 2>/dev/null | awk '{print $4}' | rg -q ":${port}$"; then
      busy="${busy} ${port}"
    fi
  done
  if [[ -n "${busy}" ]]; then
    echo "ERROR: ${label} ports already in use:${busy}" >&2
    return 1
  fi
  echo "OK: ${label} ports free"
}

WAH_CASES_JSON="/data/zmy/OurAgent-he1/benchmark/datasets/extracted/reactree/wah/cases.json"
WAH_CASE_IDS_FILE="${LOG_ROOT}/wah_case_ids_100_tasklevel.txt"
jq -r '.cases[] | select(.case_id | test(":0$")) | .case_id' "${WAH_CASES_JSON}" > "${WAH_CASE_IDS_FILE}"
if [[ "$(wc -l < "${WAH_CASE_IDS_FILE}")" != "100" ]]; then
  echo "ERROR: WAH task-level case id count is not 100" >&2
  exit 1
fi

echo "===== START QWEN36 LANE $(date -u '+%Y-%m-%d %H:%M:%S UTC') =====" | tee -a "${LOG_ROOT}/queue.log"
require_model 18003 Qwen3.6-27B || exit 1

run_step delta_bare_full_qwen36_20260817 \
  "${PYBIN}" benchmark/delta/bare_baseline/code/run.py \
    --run-name delta_bare_full_qwen36_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --resume

run_step eai_virtualhome_bare_full_qwen36_20260817 \
  "${PYBIN}" benchmark/eai/virtualhome/bare_baseline/code/run.py \
    --run-name eai_virtualhome_bare_full_qwen36_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --resume

require_free_ports qwen36-wah-unity 9910 9911 9912 9913 9914 || exit 1
run_step reactree_wah_bare_full_qwen36_official_100_20260817 \
  "${PYBIN}" benchmark/reactree/wah/bare_baseline/code/run.py \
    --run-name reactree_wah_bare_full_qwen36_official_100_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --case-ids-file "${WAH_CASE_IDS_FILE}" \
    --official-base-port 9910 \
    --official-port-ids 0 1 2 3 4 \
    --official-timeout-s 180 \
    --full-observable \
    --resume

run_step reactree_alfred_bare_full_qwen36_seen_20260817 \
  "${PYBIN}" benchmark/reactree/alfred/bare_baseline/code/run.py \
    --run-name reactree_alfred_bare_full_qwen36_seen_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --eval-set valid_seen \
    --x-displays 98 99 100 101 102 \
    --resume

run_step reactree_alfred_bare_full_qwen36_unseen_20260817 \
  "${PYBIN}" benchmark/reactree/alfred/bare_baseline/code/run.py \
    --run-name reactree_alfred_bare_full_qwen36_unseen_20260817 \
    --workers 5 \
    --ports 18003 \
    --api-model Qwen3.6-27B \
    --api-key qwen-local-key \
    --eval-set valid_unseen \
    --x-displays 108 109 110 111 112 \
    --resume

echo "===== QWEN36 LANE ALL DONE $(date -u '+%Y-%m-%d %H:%M:%S UTC') =====" | tee -a "${LOG_ROOT}/queue.log"
