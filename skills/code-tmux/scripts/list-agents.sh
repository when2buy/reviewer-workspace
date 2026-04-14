#!/bin/bash
set -euo pipefail

# List all code agent tmux sessions (live view)
# For full tracking with task details, use: status-agents.sh
# Usage: list-agents.sh

echo "📋 Live code agent sessions (tmux):"
echo ""

if ! tmux list-sessions &>/dev/null; then
  echo "❌ No tmux sessions running"
  exit 0
fi

count=0
while IFS=: read -r session rest; do
  agent_type=$(echo "$session" | cut -d'-' -f2)
  created=$(tmux display -p -t "$session" -F "#{session_created}" 2>/dev/null || echo "")
  if [[ -n "$created" ]]; then
    created_readable=$(date -d "@$created" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -r "$created" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "unknown")
  else
    created_readable="unknown"
  fi

  echo "🤖 $session  [$agent_type]  created: $created_readable"
  echo "   Attach : tmux attach -t \"$session\""
  echo "   Output : tmux capture-pane -p -t \"$session\" -S -200"
  echo ""
  count=$((count + 1))
done < <(tmux list-sessions 2>/dev/null | grep '^code-')

if [[ $count -eq 0 ]]; then
  echo "📊 No code agent sessions found"
  echo ""
  echo "💡 All tmux sessions:"
  tmux list-sessions 2>/dev/null || echo "   (none)"
else
  echo "📊 Total: $count session(s)"
  echo ""
  echo "💡 For full task tracking: $(dirname "$0")/status-agents.sh"
fi
