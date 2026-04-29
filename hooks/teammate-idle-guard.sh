#!/bin/bash
set -euo pipefail

INPUT="$(cat)"

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // "."')"
TEAMMATE_NAME="$(printf '%s' "$INPUT" | jq -r '.teammate_name // "teammate"')"

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

if grep -Eq 'status:\s*queued' "$DISPATCH_BOARD"; then
  echo "$TEAMMATE_NAME: queued units still exist in DISPATCH_BOARD.md. Claim the next eligible unit or report the blocker to the lead instead of going idle." >&2
  exit 2
fi

exit 0
