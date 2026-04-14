#!/bin/bash
set -euo pipefail

# Spawn code agent in tmux with auto-approval + task tracking
# Usage: spawn-agent.sh <agent> "<task>" [workdir]

AGENT="${1:-claude}"
TASK="${2:?Task required}"
WORKDIR="${3:-.}"

# Tracking directory
TRACK_DIR="${CODE_AGENT_TRACK_DIR:-/tmp/code-agents}"
mkdir -p "$TRACK_DIR"

# Session name
TIMESTAMP=$(date +%s)
SESSION="code-${AGENT}-${TIMESTAMP}"

# Resolve workdir
WORKDIR=$(cd "$WORKDIR" && pwd)

echo "🚀 Spawning $AGENT in tmux..."
echo "   Task: $TASK"
echo "   Workdir: $WORKDIR"
echo "   Session: $SESSION"
echo ""

# Write task record to tasks.jsonl
TASK_RECORD=$(printf '{"session":"%s","agent":"%s","task":"%s","workdir":"%s","started_at":%s,"status":"running"}' \
  "$SESSION" "$AGENT" "$TASK" "$WORKDIR" "$TIMESTAMP")
echo "$TASK_RECORD" >> "$TRACK_DIR/tasks.jsonl"

# Create log file for this session
LOG_FILE="$TRACK_DIR/${SESSION}.log"
echo "=== Task: $TASK ===" > "$LOG_FILE"
echo "=== Agent: $AGENT | Workdir: $WORKDIR ===" >> "$LOG_FILE"
echo "=== Started: $(date -d "@$TIMESTAMP" '+%Y-%m-%d %H:%M:%S UTC' 2>/dev/null || date -r "$TIMESTAMP" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date) ===" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# Create tmux session (default server)
tmux new-session -d -s "$SESSION" -c "$WORKDIR"

# Build agent command with auto-approval flags
case "$AGENT" in
  claude)
    CMD="claude --dangerously-skip-permissions exec \"$TASK\""
    ;;
  codex)
    CMD="codex --yolo exec \"$TASK\""
    ;;
  gemini)
    if gemini --help 2>&1 | grep -q "auto-approve"; then
      CMD="gemini exec --auto-approve \"$TASK\""
    else
      CMD="gemini exec \"$TASK\""
      echo "⚠️  Gemini auto-approve not confirmed, may prompt for permissions"
    fi
    ;;
  *)
    echo "❌ Unknown agent: $AGENT"
    echo "   Supported: claude, codex, gemini"
    # Remove incomplete task record
    sed -i "/$SESSION/d" "$TRACK_DIR/tasks.jsonl" 2>/dev/null || true
    exit 1
    ;;
esac

# Wrap command: tee output to log, write .done or .failed on exit
DONE_FILE="$TRACK_DIR/${SESSION}.done"
FAIL_FILE="$TRACK_DIR/${SESSION}.failed"

WRAPPED_CMD="{ ${CMD}; } 2>&1 | tee -a \"${LOG_FILE}\"; EXIT_CODE=\${PIPESTATUS[0]}; FINISHED_AT=\$(date +%s); if [ \$EXIT_CODE -eq 0 ]; then echo \$FINISHED_AT > \"${DONE_FILE}\"; echo '\\n✅ Task completed' >> \"${LOG_FILE}\"; else echo \$FINISHED_AT > \"${FAIL_FILE}\"; echo '\\n❌ Task failed (exit '\$EXIT_CODE')' >> \"${LOG_FILE}\"; fi"

# Send command to tmux
tmux send-keys -t "$SESSION" -l -- "$WRAPPED_CMD" && \
  sleep 0.2 && \
  tmux send-keys -t "$SESSION" Enter

echo "✅ Agent spawned!"
echo ""
echo "📺 Monitor:"
echo "   tmux attach -t \"$SESSION\""
echo ""
echo "📊 Track status:"
echo "   $(dirname "$0")/status-agents.sh"
echo ""
echo "📄 Live log:"
echo "   tail -f \"$LOG_FILE\""
echo ""
echo "🛑 Kill session:"
echo "   tmux kill-session -t \"$SESSION\""
echo ""
