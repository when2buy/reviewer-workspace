# Skills used by Grim

This directory vendors the main AgentSkills used by the reviewer workspace so the setup is reproducible from the repo.

## Included skills

- `code-review` — primary PR/code review workflow
- `github` — GitHub operations via `gh`
- `github-access` — local GitHub auth and repo access notes
- `code-tmux` — run code agents in tmux when needed
- `coding-agent` — delegate larger coding tasks to ACP/subagents
- `tmux` — interact with tmux sessions
- `skill-creator` — maintain and improve skills
- `clawhub` — install/update/publish skills from clawhub

## Notes

- These are vendored snapshots from local OpenClaw skill directories.
- Some skills are user-local (`~/.openclaw/skills/*`), others come from the OpenClaw install.
- Secrets should stay out of repo. If a skill contains sensitive local details, sanitize before pushing.
