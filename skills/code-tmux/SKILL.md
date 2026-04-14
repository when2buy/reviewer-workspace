---
name: code-tmux
description: "Invoke code agents (Claude Code, Codex, Gemini) in tmux with auto-approval for code generation tasks. Use when user asks to write, refactor, or fix code. Agents run with full permissions in tmux for monitoring."
metadata:
  {
    "openclaw": {
      "emoji": "💻",
      "requires": {
        "anyBins": ["claude", "codex", "gemini"],
        "bins": ["tmux"]
      }
    }
  }
---

# Code Agent via Tmux (Auto-Approve)

Spawn code agents (Claude Code, Codex, Gemini) in **tmux** with **full auto-approval** for code generation tasks.

## Why This Skill?

- **Auto-approve**: Skips permission prompts (`--dangerously-skip-permissions` / `--approve-all`)
- **Tmux monitoring**: User can attach and watch progress
- **Model strategy**: Strong model for planning (opus), weaker for execution (sonnet/haiku)
- **No manual coding**: Delegate code writing to specialized agents

## Quick Start

### Spawn agent for a coding task

```bash
{baseDir}/scripts/spawn-agent.sh <agent> "<task>" [workdir]
```

**Examples:**

```bash
# Claude Code with auto-approve
{baseDir}/scripts/spawn-agent.sh claude "Add error handling to API calls" ~/myproject

# Codex in current directory
{baseDir}/scripts/spawn-agent.sh codex "Refactor database queries" .

# Gemini for a new feature
{baseDir}/scripts/spawn-agent.sh gemini "Build a login page" ~/frontend
```

**What it does:**
1. Creates isolated tmux session
2. Launches agent with `--dangerously-skip-permissions` or equivalent
3. Returns tmux attach command for monitoring
4. Agent runs with auto-approval (no prompts)

### Monitor the agent

```bash
# Attach to watch live progress
tmux attach -t <session>

# Detach: Ctrl+b d

# Check output without attaching
tmux capture-pane -p -t <session> -S -200

# List all tmux sessions
tmux ls
```

### Track all tasks (global status)

```bash
# Show all active/failed tasks with status
{baseDir}/scripts/status-agents.sh

# Show ALL tasks including completed ones
{baseDir}/scripts/status-agents.sh --all

# Live log for a specific session
tail -f /tmp/code-agents/<session>.log
```

**Task tracking files** (stored in `/tmp/code-agents/` by default):
```
/tmp/code-agents/
├── tasks.jsonl                  # append-only task log (one JSON record per line)
├── code-claude-<ts>.log         # full output log per session
├── code-claude-<ts>.done        # created on success (contains finish timestamp)
└── code-claude-<ts>.failed      # created on failure (contains finish timestamp)
```

Override tracking dir: `export CODE_AGENT_TRACK_DIR=~/my-track-dir`

### Agent-specific flags

**Claude Code:**
```bash
claude --dangerously-skip-permissions exec "<task>"
```

**Codex:**
```bash
codex --yolo exec "<task>"
# or
codex --approve-all exec "<task>"
```

**Gemini (if supported):**
```bash
gemini exec --auto-approve "<task>"
```

## Model Strategy

**Planning phase (strong model):**
- `opus` (Claude Opus 4.6)
- `o1` (OpenAI o1)

**Execution phase (efficient model):**
- `sonnet` (Claude Sonnet 4.5)
- `haiku` (Claude Haiku 4.5)
- `gpt-4o-mini`

**Switch models during execution:**
```bash
# In Claude Code
/model sonnet

# In Codex
/model haiku
```

**Check available models:**
```bash
claude
/model

codex
/model
```

## Tmux Session Management

**Uses default tmux server** - Easy to find with `tmux ls`

**Session naming pattern:**
```bash
code-<agent>-<timestamp>
# Example: code-claude-1708123456
```

**List all sessions:**
```bash
tmux ls                          # All tmux sessions
{baseDir}/scripts/list-agents.sh  # Only code agents
```

**Kill a session:**
```bash
tmux kill-session -t <session>
```

## Safety Notes

⚠️ **Auto-approval bypasses safety checks**
- Use in trusted projects only
- Review code after agent finishes
- Don't run on production code without review

✅ **When to use:**
- Prototyping
- Refactoring
- Boilerplate generation
- Bug fixes in isolated features

❌ **When NOT to use:**
- Production deployments
- Security-sensitive code
- Database migrations
- System configuration

## Workflow Example

**User request:** "Write a REST API for user authentication"

**Agent spawns:**
```bash
{baseDir}/scripts/spawn-agent.sh claude "Build REST API for user auth with JWT" ~/backend
```

**Agent runs:**
1. Planning with `opus` (architecture decisions)
2. Switch to `sonnet` for implementation
3. Auto-approves all file edits (no prompts)
4. User monitors via tmux attach

**Completion:**
```bash
# Check final state
tmux capture-pane -p -t code-claude-1708123456 -S -50

# Review generated code
cd ~/backend && git diff
```

## Troubleshooting

**Agent hangs waiting for approval:**
- Check if `--dangerously-skip-permissions` is in the command
- For Codex, ensure `--yolo` or `--approve-all` flag

**Tmux session not found:**
```bash
# List all sessions
tmux ls

# Check if tmux server is running
tmux list-sessions 2>&1 || echo "No tmux server running"
```

**Git repo required (Codex):**
```bash
# Codex refuses to run outside git repos
cd /tmp/scratch && git init
```

## References

- [coding-agent skill](/usr/lib/node_modules/openclaw/skills/coding-agent/SKILL.md) - Base PTY/background patterns
- [tmux skill](/usr/lib/node_modules/openclaw/skills/tmux/SKILL.md) - Tmux control details
