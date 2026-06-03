#!/bin/bash
set -euo pipefail

INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

COMMAND="$(printf '%s' "$INPUT" | jq -r '.tool_input.command // ""')"

if [[ "${HELIX_RESOURCE_GUARD_BYPASS:-0}" == "1" ]]; then
  exit 0
fi

is_pytest=0
if printf '%s' "$COMMAND" | grep -Eq '(^|[ ;|&])python3? -m pytest\b|(^|[ ;|&])pytest\b'; then
  is_pytest=1
fi

is_expensive=0
if [[ "$is_pytest" == "1" ]] && ! printf '%s' "$COMMAND" | grep -Eq 'tests/[^ ]+\.py| -k |--maxfail=|--lf|--ff'; then
  is_expensive=1
fi

if [[ "$is_pytest" == "0" ]]; then
  exit 0
fi

max_pytest="${HELIX_MAX_PARALLEL_PYTEST:-2}"
running_pytest="$(
  { pgrep -fl 'python[^ ]* -m pytest|[ /]pytest( |$)' 2>/dev/null || true; } \
    | awk '!/resource-guard.sh/ {count++} END {print count + 0}'
)"

if [[ "$running_pytest" =~ ^[0-9]+$ ]] && (( running_pytest >= max_pytest )); then
  echo "BLOCKED: $running_pytest pytest process(es) already running. Limit is HELIX_MAX_PARALLEL_PYTEST=$max_pytest." >&2
  echo "Use a focused test, wait for existing tests, or set HELIX_RESOURCE_GUARD_BYPASS=1 intentionally." >&2
  exit 2
fi

if command -v vm_stat >/dev/null 2>&1; then
  free_mb="$(
    vm_stat | awk '
      /page size of/ {gsub(/[^0-9]/, "", $8); page=$8}
      /Pages free/ {gsub(/\./, "", $3); free=$3}
      /Pages inactive/ {gsub(/\./, "", $3); inactive=$3}
      END {
        if (page == "" || page == 0) page=4096;
        printf "%.0f", ((free + inactive) * page) / 1024 / 1024
      }'
  )"
  min_free_mb="${HELIX_MIN_FREE_MEM_MB:-1024}"
  if [[ "$free_mb" =~ ^[0-9]+$ ]] && (( free_mb < min_free_mb )); then
    echo "BLOCKED: low available memory (${free_mb}MB < ${min_free_mb}MB). Not starting pytest." >&2
    exit 2
  fi
fi

if [[ "$is_expensive" == "1" ]]; then
  echo "BLOCKED: broad pytest run detected. Start with a focused test file, -k filter, --lf/--ff, or --maxfail=1." >&2
  echo "Override only if intentional: HELIX_RESOURCE_GUARD_BYPASS=1 <command>" >&2
  exit 2
fi

exit 0
