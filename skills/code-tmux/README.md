# Code-Tmux Skill

**Purpose**: Spawn code agents (Claude Code, Codex, Gemini) in tmux with auto-approval for code generation.

## Quick Examples

### Spawn Claude Code for API development
```bash
/root/clawd/skills/code-tmux/scripts/spawn-agent.sh claude "Build REST API for user authentication" ~/backend
```

### Spawn Codex for refactoring
```bash
/root/clawd/skills/code-tmux/scripts/spawn-agent.sh codex "Refactor database queries to use prepared statements" ~/myproject
```

### Spawn Gemini for frontend
```bash
/root/clawd/skills/code-tmux/scripts/spawn-agent.sh gemini "Create a responsive login page with Tailwind CSS" ~/frontend
```

### List running agents
```bash
/root/clawd/skills/code-tmux/scripts/list-agents.sh
```

### Monitor agent progress
```bash
# List all sessions (code agents start with 'code-')
tmux ls

# Attach to tmux session (Ctrl+b d to detach)
tmux attach -t code-claude-1708123456

# Check output without attaching
tmux capture-pane -p -t code-claude-1708123456 -S -200
```

## Key Features

- ✅ **Auto-approval**: Agents run with `--dangerously-skip-permissions` / `--yolo`
- ✅ **Tmux monitoring**: User can attach and watch real-time progress
- ✅ **Easy to find**: Uses default tmux server, visible with `tmux ls`
- ✅ **Model flexibility**: Switch models mid-session (`/model sonnet`)
- ✅ **Isolated sessions**: Each task runs in separate tmux session

## Model Strategy

**Planning (strong model):**
- `opus` - Claude Opus 4.6
- `o1` - OpenAI o1

**Execution (efficient model):**
- `sonnet` - Claude Sonnet 4.5
- `haiku` - Claude Haiku 4.5

See [references/models.md](references/models.md) for detailed model guide.

## Safety

⚠️ **Auto-approval bypasses safety checks**
- Use in trusted projects only
- Review code after completion
- Don't use on production code without review

## Created

2026-02-16 - Initial version based on Steve's requirements
