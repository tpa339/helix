#!/bin/bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  helix_process_guard.sh status
  helix_process_guard.sh kill-pytest
  helix_process_guard.sh kill-old-pytest [minutes]

Shows or stops pytest processes spawned by agent/tool runs.
EOF
}

cmd="${1:-status}"

case "$cmd" in
  status)
    pgrep -fl 'python[^ ]* -m pytest|[ /]pytest( |$)' || true
    ;;
  kill-pytest)
    pids="$(pgrep -f 'python[^ ]* -m pytest|[ /]pytest( |$)' || true)"
    if [[ -z "$pids" ]]; then
      echo "No pytest processes found."
      exit 0
    fi
    echo "$pids" | xargs kill
    echo "Sent TERM to pytest processes:"
    echo "$pids"
    ;;
  kill-old-pytest)
    minutes="${2:-20}"
    now="$(date +%s)"
    killed=0
    while read -r pid start; do
      [[ -z "${pid:-}" || -z "${start:-}" ]] && continue
      age_min=$(( (now - start) / 60 ))
      if (( age_min >= minutes )); then
        kill "$pid" 2>/dev/null || true
        echo "Sent TERM to old pytest pid=$pid age=${age_min}m"
        killed=1
      fi
    done < <(ps -axo pid,lstart,command | awk '/python.* -m pytest|[ /]pytest( |$)/ && !/awk/ {
      cmd_start=8;
      month=$2; day=$3; time=$4; year=$6;
      cmd="";
      for (i=7;i<=NF;i++) cmd=cmd " " $i;
      print $1, month, day, time, year
    }' | while read -r pid month day time year; do
      start="$(date -j -f "%b %d %T %Y" "$month $day $time $year" +%s 2>/dev/null || echo 0)"
      echo "$pid $start"
    done)
    if (( killed == 0 )); then
      echo "No pytest process older than ${minutes}m found."
    fi
    ;;
  *)
    usage
    exit 2
    ;;
esac
