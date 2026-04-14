#!/bin/bash
# Global status of all code agent tasks
# Usage: status-agents.sh [--all]

TRACK_DIR="${CODE_AGENT_TRACK_DIR:-/tmp/code-agents}"
SHOW_ALL="${1:-}"

if [[ ! -f "$TRACK_DIR/tasks.jsonl" ]]; then
  echo "📋 No tasks recorded yet."
  echo "   Tasks are tracked in: $TRACK_DIR/tasks.jsonl"
  exit 0
fi

NOW=$(date +%s)

echo "╔══════════════════════════════════════════════════════════╗"
echo "║              Code Agent Task Tracker                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

running=0
done=0
failed=0
total=0

while IFS= read -r line; do
  [[ -z "$line" ]] && continue

  # Parse JSON fields (simple grep-based, no jq required)
  session=$(echo "$line" | grep -oP '"session":"\K[^"]+')
  agent=$(echo "$line"   | grep -oP '"agent":"\K[^"]+')
  task=$(echo "$line"    | grep -oP '"task":"\K[^"]+')
  workdir=$(echo "$line" | grep -oP '"workdir":"\K[^"]+')
  started=$(echo "$line" | grep -oP '"started_at":\K[0-9]+')

  total=$((total + 1))

  # Determine status
  DONE_FILE="$TRACK_DIR/${session}.done"
  FAIL_FILE="$TRACK_DIR/${session}.failed"
  LOG_FILE="$TRACK_DIR/${session}.log"

  if [[ -f "$DONE_FILE" ]]; then
    STATUS="✅ done"
    finished_at=$(cat "$DONE_FILE" 2>/dev/null || echo "")
    elapsed=$((finished_at - started))
    time_info="finished in ${elapsed}s"
    done=$((done + 1))
    [[ -z "$SHOW_ALL" ]] && continue  # Skip done tasks unless --all
  elif [[ -f "$FAIL_FILE" ]]; then
    STATUS="❌ failed"
    finished_at=$(cat "$FAIL_FILE" 2>/dev/null || echo "")
    elapsed=$((finished_at - started))
    time_info="failed after ${elapsed}s"
    failed=$((failed + 1))
  else
    # Check if tmux session still alive
    if tmux has-session -t "$session" 2>/dev/null; then
      STATUS="🔄 running"
      elapsed=$((NOW - started))
      time_info="running for ${elapsed}s"
    else
      STATUS="⚠️  orphaned"
      elapsed=$((NOW - started))
      time_info="session gone, started ${elapsed}s ago"
    fi
    running=$((running + 1))
  fi

  # Format start time
  started_fmt=$(date -d "@$started" '+%m-%d %H:%M:%S' 2>/dev/null || date -r "$started" '+%m-%d %H:%M:%S' 2>/dev/null || echo "$started")

  # Truncate task display
  task_display="${task:0:60}"
  [[ ${#task} -gt 60 ]] && task_display="${task_display}..."

  echo "┌─ $STATUS  [$agent]  $started_fmt"
  echo "│  Session : $session"
  echo "│  Task    : $task_display"
  echo "│  Workdir : $workdir"
  echo "│  Time    : $time_info"
  if [[ -f "$LOG_FILE" ]]; then
    echo "│  Log     : $LOG_FILE"
    # Show last 2 lines of log (latest activity)
    last_lines=$(tail -2 "$LOG_FILE" 2>/dev/null | sed 's/^/│  » /')
    echo "$last_lines"
  fi
  if [[ "$STATUS" == "🔄 running" ]]; then
    echo "│  Monitor : tmux attach -t \"$session\""
  fi
  echo "└──────────────────────────────────────────────────────────"
  echo ""

done < "$TRACK_DIR/tasks.jsonl"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Total: $total  |  Running: $running  |  Done: $done  |  Failed: $failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [[ $running -eq 0 && -z "$SHOW_ALL" ]]; then
  echo "💡 No active tasks. Run with --all to see completed tasks."
fi
