#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="${OURAGENT_WORKSPACE_ROOT:-/data/zmy}"
PYBIN="${OURAGENT_PYTHON:-${WORKSPACE_ROOT}/envs/ouragent/bin/python}"

unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY all_proxy
exec "${PYBIN}" "${HERE}/run.py" "$@"

