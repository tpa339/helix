#!/bin/bash
set -euo pipefail

INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

TASK_SUBJECT="$(printf '%s' "$INPUT" | jq -r '.task_subject // ""')"
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // "."')"
UNIT_ID="$(printf '%s' "$TASK_SUBJECT" | sed -n 's/^\(\[U-[0-9]\{3\}\]\).*/\1/p')"

if [[ -z "$UNIT_ID" ]]; then
  echo "Completed task must map to a unit id like [U-001]." >&2
  exit 2
fi

DISPATCH_BOARD=""
for candidate in \
  "$CWD/.helix/state/DISPATCH_BOARD.md" \
  "$CWD/DISPATCH_BOARD.md"
do
  if [[ -f "$candidate" ]]; then
    DISPATCH_BOARD="$candidate"
    break
  fi
done

if [[ -z "$DISPATCH_BOARD" ]]; then
  exit 0
fi

if ! grep -qF "$UNIT_ID" "$DISPATCH_BOARD"; then
  echo "Unit $UNIT_ID is not present in DISPATCH_BOARD.md. Update the dispatch board before completing the task." >&2
  exit 2
fi

STATUS_BLOCK="$(awk -v unit="$UNIT_ID" '
  $0 ~ unit {capture=1; print; next}
  capture && /^### / {exit}
  capture {print}
' "$DISPATCH_BOARD")"

if ! printf '%s\n' "$STATUS_BLOCK" | grep -Eq 'status:\s*(review_ready|validated|integrated)'; then
  echo "Unit $UNIT_ID is not yet marked review_ready, validated, or integrated in DISPATCH_BOARD.md. Update status and verification trail before completing." >&2
  exit 2
fi

exit 0
