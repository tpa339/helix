#!/bin/bash
set -euo pipefail

INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

TASK_SUBJECT="$(printf '%s' "$INPUT" | jq -r '.task_subject // ""')"
TASK_DESCRIPTION="$(printf '%s' "$INPUT" | jq -r '.task_description // ""')"

if [[ -z "$TASK_SUBJECT" ]]; then
  echo "Task subject is required." >&2
  exit 2
fi

if [[ ! "$TASK_SUBJECT" =~ ^\[U-[0-9]{3}\]\  ]]; then
  echo "Task subject must start with a stable work-unit id like '[U-001] Implement auth flow'." >&2
  exit 2
fi

if [[ -z "$TASK_DESCRIPTION" || "$TASK_DESCRIPTION" == "null" ]]; then
  echo "Task description is required. Include boundaries, files, and verification intent." >&2
  exit 2
fi

exit 0
