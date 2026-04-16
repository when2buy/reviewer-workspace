# Reviewer Reference Files

These files are the current review guidance and local reviewer context used in the workspace.

Included:
- `SKILL.md`
- `review-checklist.md`
- `finbench-standards.md`
- `anti-patterns.md`
- `examples-finbench-review.md`

Source of truth for the vendored skill copy during inspection:
- `/home/node/.openclaw/skills/code-review/`

Harbor-specific review stance captured here:
- If agents cannot access `/tests` at runtime, visible verifier logic is **not** treated as leakage by default.
- Default blockers should focus on runtime-relevant correctness, contract alignment, reproducibility, scope hygiene, and trustworthy grading behavior.
